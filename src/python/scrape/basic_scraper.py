import os
import threading
from typing import Any, Callable, Optional;
import requests;
from io import BytesIO
from PIL import Image;
from math import ceil;
from selectolax.parser import HTMLParser, Node
from models.story_type import StoryType
from models.scraper_result import ScraperResult
from models.joke import Joke;
from selenium.webdriver.remote.webdriver import WebDriver

class BasicConfiguration():
    def __init__(self, get_story_type: Callable[[Node, list[str]], StoryType], get_title: Callable[[Node], Node], get_buttons: Callable[[Node], Any], get_urls: Callable[[Any], Any], get_keys: Callable[[Node, list[str]], Any], get_chapter: Callable[[Node, list[str]], Node] = None, src: str =None):
        self.get_story_type = get_story_type;
        self.src = src; # manga
        self.get_chapter = get_chapter; # tts
        self.get_title = get_title;
        self.get_buttons = get_buttons;
        self.get_urls = get_urls;
        self.get_keys = get_keys;
        pass

class BasicScraper():
    def __init__(self, url, driver:WebDriver=None, session:Optional[requests.Session]=None, headers={}):
        self._url = url;
        self._headers = headers;
        self._setup_folders();
        self._result: ScraperResult = None;
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

    def get_result(self, domain=None) -> ScraperResult:
        return self._result.get_with_domain(domain);

    @staticmethod
    def get_lines(node: Node, depth = 0):
        text = node.text(strip=True)
        if node.tag != '-text':
            childLines = []
            child = node.child;
            while child:
                childLines.extend(BasicScraper.get_lines(child, depth + 1));
                child = child.next;
            return childLines;
        elif text != "" and node.parent != None:
            return [node];
        return []

    def _get_images_from_tags(self, img_tags=[], src='src'):
        img_urls = [];
        for img_tag in img_tags:
            if src in img_tag.attributes:
                img_urls.append(img_tag.attributes[src]);
        return self._get_images(img_urls);

    def _get_images(self, img_urls: list[str] = [], retry=0):
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

    def _get_image_async(self, images: list, img_url):
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
            success = self._extract_image(images, img_file, ext);
            if success:
                break;

    def _extract_image(self, images: list, img_file, ext) -> bool:
        try:
            url_img = Image.open(img_file if isinstance(img_file, str) else BytesIO(img_file))
            url_img_width, url_img_height = url_img.size;
            parts = ceil(url_img_height / 10000);
            for partIndex in range(parts):
                startY = partIndex * 10000;
                part_height = (url_img_height % 10000 if partIndex == parts - 1 else 10000) or 10000;
                cropped_url_img = url_img.crop((0, startY, url_img_width, startY + part_height));
                img_byte_arr = BytesIO();
                _ext = ext.upper()[1:];
                cropped_url_img.save(img_byte_arr, format='JPEG' if _ext == 'JPG' else _ext);
                images.append(img_byte_arr.getvalue());
            return True;
        except Exception as e:
            print('error', e);
            return False;

    def _try_get_json(self, url, session:requests.Session, headers={}):
        result = self._try_get_response(url, session, headers);
        if result is not None:
            return result.json();

    def _try_get_response(self, url:str, session:Optional[requests.Session], headers={}, setResult=True):
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
            self._result = BasicScraper._get_error(error, self._url, True);

    @staticmethod
    def _get_default_tts(texts: list, title: str, url:str, next_url: Optional[str] = None, loading=False, driver_required=False, driver_requires_reset=False):
        spans =  map(lambda x: f"<div>{x}</div>", texts);
        chapter = HTMLParser(f"<div>{''.join(spans)}</div>").body.child;
        return ScraperResult(
            story_type=StoryType.NOVEL,
            urls = BasicScraper.Object(prev=None, current = url, next=next_url),
            chapter = chapter,
            lines = BasicScraper.get_lines(chapter),
            title = title,
            keys = BasicScraper.Object(story=None, chapter=None),
            loading = loading,
            driver_required = driver_required,
            driver_requires_reset = driver_requires_reset,
        )

    @staticmethod
    def _get_error(error, url, loading=False):
        print('An error occurred while parsing the url!', 'Url:', url, 'Error:', error);
        return BasicScraper._get_default_tts(
            texts = ['An error occurred while parsing the url!', 'Url:', url, 'Error:', str(error)],
            title = 'An error occurred while parsing the url!',
            url = url,
            loading=loading);

    @staticmethod
    def _get_cannot_parse(url, driver_requires_reset=False):
        return BasicScraper._get_default_tts(
            texts = ['Failed to parse content of the url!', 'Url:', url],
            title = 'Cannot parse the url!',
            url = url,
            next_url=url if driver_requires_reset else None,
            driver_requires_reset=driver_requires_reset);
    
    @staticmethod
    def _get_waiting(url: str, next_url: str):
        joke = Joke();
        return BasicScraper._get_default_tts(
            texts = ['Loading', joke.type] + joke.texts,
            title = 'Loading site',
            url = url,
            next_url = next_url,
            loading = True);
    
    @staticmethod
    def _get_driver_required(url: str):
        joke = Joke();
        return BasicScraper._get_default_tts(
            texts = ['Loading', joke.type] + joke.texts,
            title = 'Starting driver for website',
            url = url,
            next_url = url,
            driver_required = True);
    
    @staticmethod
    def _get_driver_requires_reset(url: str):
        joke = Joke();
        return BasicScraper._get_default_tts(
            texts = ['Resetting', joke.type] + joke.texts,
            title = 'Starting driver for website',
            url = url,
            next_url = url,
            driver_required = True,
            driver_requires_reset = True);

