import os
import threading
from typing import Callable, Optional, Union;
import requests;
from io import BytesIO
from PIL import Image;
from math import ceil;
from selectolax.parser import HTMLParser, Node
from helpers.story_type import StoryType
from helpers.scraper_result import ScraperResult, KeyResult, UrlResult
from helpers.joke import Joke;
from selenium.webdriver.remote.webdriver import WebDriver

class BasicConfiguration():
    def __init__(self, get_story_type: Callable[[Node, list[str]], StoryType], get_titles: Callable[[Node, list[str]], KeyResult], get_urls: Callable[[Node, list[str]], UrlResult], get_keys: Callable[[Node, list[str]], KeyResult], get_chapter: Callable[[Node, list[str]], Node]|None = None, src: Union[str, Callable[[Node], str]]|None = None):
        self.get_story_type = get_story_type;
        self.src = src; # manga
        self.get_chapter = get_chapter; # tts
        self.get_titles = get_titles;
        self.get_urls = get_urls;
        self.get_keys = get_keys;
        pass

class BasicScraper():
    def __init__(self, url: str, driver:WebDriver|None=None, session:requests.Session|None=None, headers={}):
        self._url = url;
        self._headers = headers;
        self._setup_folders();
        self._result: ScraperResult|None = None;
        self._driver = driver;
        self._session = session;
        pass

    def _setup_folders(self):
        self._base_download_path = "./downloads"
        self._html_download_path = f"{self._base_download_path}/html"
        self._zip_download_path = f"{self._base_download_path}/zip"

        if not os.path.exists(self._base_download_path):
            os.makedirs(self._base_download_path); 
            os.makedirs(self._zip_download_path); 
            os.makedirs(self._html_download_path);

    @staticmethod
    def Object(**kwargs):
        return type("Object", (), kwargs);

    def get_result(self, domain: str|None = None) -> ScraperResult:
        return self._result is not None and self._result.get_with_domain(domain) or ScraperResult._get_error('Missing ScraperResult', self._url);

    def get_children(node: Node):
        children = [];
        child = node.child;
        while child:
            children.append(child);
            child = child.next;
        return children;

    def _get_images_from_tags(self, img_tags: list[Node]=[], src = 'src'):
        img_urls = [];
        for img_tag in img_tags:
            if callable(src):
                img_urls.append(src(img_tag));
            elif src in img_tag.attributes and img_tag.attributes[src]:
                img_urls.append(img_tag.attributes[src]);
        return self._get_images(img_urls);

    def _get_images(self, img_urls: list[str] = [], retry = 0):
        threads, images = self._get_image_threads(img_urls)
        for thread in threads:
            thread.start();
        for thread in threads:
            thread.join();
        self._handle_failure_and_logging(img_urls, images, retry);
        return [image for image_sublist in images for image in image_sublist];

    def _handle_failure_and_logging(self, img_urls: list[str], images: list, retry: int):
        if all([True if len(x) == 0 else False for x in images]) and retry < 2:
            print(f'Retry fetcing images, {retry + 1} attempt');
            return self._get_images(img_urls, retry + 1);
        for i,x in enumerate(images):
            if len(x) == 0:
                print(f'Failed to parse image {i+1} of {len(images)} images from the url: {img_urls[i]}');

    def _get_image_threads(self, img_urls: list[str]):
        threads: list[threading.Thread] = [];
        images = [];
        for img_url in img_urls:
            img_url = img_url.strip();
            if not img_url.startswith('http'): continue;
            image_list: list[bytes] = []
            images.append(image_list);
            t = threading.Thread(target=self._get_image_async, args=(image_list, img_url), daemon=False);
            threads.append(t);
        return threads, images;

    def _get_image_async(self, images: list, img_url: str):
        url_no_params = img_url.split('?')[0];
        file_name, ext = os.path.splitext(url_no_params);
        merged_headers = dict();
        merged_headers.update({
            "Accept": f"image/webp,image/{ext[1:]}",
            "Host": img_url.split("/")[2],
            "Referer": "/".join(self._url.split("/")[:5]),
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
        });
        merged_headers.update(self._headers);
        for i in range(3):
            response = self._try_get_response(img_url, self._session, merged_headers, False)
            if not response or not response.ok: 
                continue;
            img_file = response.content
            img_type = response.headers["Content-Type"].split("/")[-1];
            if img_type == 'error':
                continue;
            success = self._extract_image(images, img_file, img_type);
            if success:
                break;

    def _extract_image(self, images: list, img_file: bytes, ext: str) -> bool:
        try:
            url_img = Image.open(img_file if isinstance(img_file, str) else BytesIO(img_file)).convert('RGB')
            url_img_width, url_img_height = url_img.size;
            parts = ceil(url_img_height / 10000);
            for partIndex in range(parts):
                startY = partIndex * 10000;
                part_height = (url_img_height % 10000 if partIndex == parts - 1 else 10000) or 10000;
                cropped_url_img = url_img.crop((0, startY, url_img_width, startY + part_height));
                img_byte_arr = BytesIO();
                _ext = ext.upper().replace('.', '');
                cropped_url_img.save(img_byte_arr, format='JPEG' if _ext == 'JPG' else _ext);
                images.append(img_byte_arr.getvalue());
            return True;
        except Exception as e:
            print('error', e);
            return False;

    def _try_get_json(self, url: str, session: requests.Session, headers = {}):
        result = self._try_get_response(url, session, headers);
        if result is not None:
            return result.json();

    def _try_get_response(self, url: str, session: Optional[requests.Session], headers = {}, setResult = True):
        error = "";
        try:
            if session:
                return session.get(url, headers=headers);
            else:
                return requests.get(url, headers=headers);
        except requests.exceptions.ConnectionError as e:
            error = 'A connection error occured during the request';
        except requests.exceptions.Timeout as e:
            error = 'A timeout error occured during the request';
        except requests.exceptions.TooManyRedirects as e:
            error = 'A "too many redirects" error occured during the request';
        except requests.exceptions.RequestException as e:
            error = 'A error occured during the request';
        if setResult:
            self._result = ScraperResult._get_error(error, self._url, True);

