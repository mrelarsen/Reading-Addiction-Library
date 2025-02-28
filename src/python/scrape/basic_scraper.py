import base64
import os
import threading
from typing import Callable, Optional, Union;
import requests;
from io import BytesIO
from PIL import Image;
from math import ceil;
from selectolax.parser import Node
from helpers.story_type import StoryType
from helpers.scraper_result import ScraperResult, KeyResult, UrlResult
from selenium.webdriver.remote.webdriver import WebDriver

class BasicConfiguration():
    def __init__(self, get_story_type: Callable[[Node, list[str]], StoryType], get_titles: Callable[[Node, list[str]], KeyResult], get_urls: Callable[[Node, list[str]], UrlResult], get_keys: Callable[[Node, list[str]], KeyResult], get_chapter: Callable[[Node, list[str]], Node]|None = None, src: Union[str, Callable[[Node], str]]|None = None, alt_selector: str|None = None):
        self.get_story_type = get_story_type;
        self.src = src; # manga
        self.alt_selector = alt_selector; # manga
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

    @staticmethod
    def get_children(node: Node):
        children = [];
        child = node.child;
        while child:
            children.append(child);
            child = child.next;
        return children;

    def _get_images_from_tags(self, img_tags: list[Node]=[], src = 'src', img_selector = 'img'):
        img_urls = [];
        if len(img_tags) == 0:
            print("No image tags were found");
            return [];
        for img_tag in img_tags:
            if callable(src):
                img_urls.append(src(img_tag));
            elif src in img_tag.attributes and img_tag.attributes.get(src):
                img_urls.append(img_tag.attributes[src].strip());
        if len(img_urls) == 0:
            print("No images were found");
            return [];
        return self._get_images(img_urls, src, img_selector);

    def _get_images(self, img_urls: list[str] = [], src = 'src', img_selector = 'img', retry = 0):
        threads, images, errors = self._get_image_threads(img_urls, src, img_selector)
        for thread in threads:
            thread.start();
        for thread in threads:
            thread.join();
        self._handle_failure_and_logging(img_urls, src, img_selector, images, errors, retry);
        return [image for image_sublist in images for image in image_sublist];

    def _handle_failure_and_logging(self, img_urls: list[str], src, img_selector, images: list, errors: list, retry: int):
        if all([True if len(x) == 0 else False for x in images]) and retry < 2:
            if len(errors) == 0:
                print(f'No images, no errors found for {len(img_urls)} uls: [{",".join(img_urls)}]')
            else:
                for error_list in errors:
                    for error in error_list: print(f'Image error: {error}')
            print(f'Retry fetcing images, {retry + 1} attempt');
            return self._get_images(img_urls, src, img_selector, retry + 1);
        for i,x in enumerate(images):
            if len(x) == 0:
                print(f'Failed to parse image {i+1} of {len(images)} images from the url: {img_urls[i]}');
                for error in errors[i]: print(f'Image error: {error}');

    def _get_image_threads(self, img_urls: list[str], src, img_selector):
        threads: list[threading.Thread] = [];
        images = [];
        errors = [];
        for img_url in img_urls:
            img_url = img_url.strip();
            # print(f'Img url: {img_url}')
            if not img_url.startswith('http'): continue;
            
            image_list: list[bytes] = [];
            error_list: list[str] = [];
            images.append(image_list);
            errors.append(error_list);
            t = threading.Thread(target=self._get_image_async, args=(image_list, img_url, src, img_selector, error_list,), daemon=False);
            threads.append(t);
        return threads, images, errors;

    def _get_image_async(self, images: list, img_url: str, src, img_selector, errors: list):
        # errors.append(f"error start");
        url_no_params = img_url.split('?')[0];
        file_name, ext = os.path.splitext(url_no_params);
        headers = {
            "Accept": f"image/webp,image/{ext[1:]}",
            "Host": img_url.split("/")[2],
            "Referer": "/".join(self._url.split("/")[:5]),
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
        };
        for i in range(3):
            # errors.append(f"Try {i} of 3");
            if i == 0 or '_driver' not in dir(self) or not self._driver or callable(src):
                response = self._try_get_response(img_url, self._session, {**headers, **self._headers}, False);
            else:
                img_type, img_file = BasicScraper.get_image(self._driver, img_url, src, img_selector);
                errors.append(img_type);
                if not img_file or not img_type: continue;
                success = self._extract_image(images, img_file, img_type);
                if success: break;
                continue;
            if not response or not response.ok: 
                errors.append(("Response status code: " + str(response.status_code)) if response else 'Response not found');
                continue;
            # errors.append('type');
            img_file = response.content
            img_type = response.headers.get("Content-Type");
            if not img_type or img_type.split("/")[-1] == 'error':
                errors.append("Content-type: " + str(response.headers.get("Content-Type")))
                continue;
            success = self._extract_image(images, img_file, img_type.split("/")[-1]);
            if success:
                break;
            errors.append(f"Error fetching image: {img_url}")
    
    @staticmethod
    def get_image(driver: WebDriver, img_url: str, src: str, img_selector: str):
        base64string = driver.execute_script("var c = document.createElement('canvas');"
                       + "var ctx = c.getContext('2d');"
                       + f'var img = document.querySelector(`{img_selector}[{src}="{img_url}"]`);'
                       + "if (img == null) return null;"
                       + "c.height=img.naturalHeight;"
                       + "c.width=img.naturalWidth;"
                       + "ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight);"
                       + "var base64String = c.toDataURL();"
                       + "return base64String;");
        if not base64string: return None, None;
        base64Array = base64string.split(',');
        return base64Array[0].split(':')[-1], base64.b64decode(base64Array[-1]);

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

    def _try_get_json(self, url: str, session: requests.Session|None, headers = {}):
        result = self._try_get_response(url, session, headers);
        if result is not None:
            return result.json();

    def _try_get_response(self, url: str, session: requests.Session|None, headers = {}, setResult = True):
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

