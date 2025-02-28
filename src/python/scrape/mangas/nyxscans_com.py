import requests, re, json, collections.abc
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node, HTMLParser
from helpers.scraper_result import KeyResult, ScraperResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        # super().useHtml(url, headers);
        super().useDriver(url, driver, headers);
        # super().useReDriver(url, driver, headers);;
        # super().useSession(url, session_dict, headers);

    def _scrape(self, body: Node, head: Node, parser: HTMLParser):
        urls_finds = re.findall(r'<script>self.__next_f.push\(\[1,"6:(.+)"\]\)</script>', body.html);
        if len(urls_finds) == 0: return ScraperResult._get_error("This chapter is most likely payment-locked", self._url);

        # print(body.html)
        url_json = json.loads('{"content": "' + urls_finds[0] + '"}');
        url_json_content = json.loads(url_json['content']);
        images = self.findInArray(url_json_content, 'chapter.images');
        next = self.findInArray(url_json_content, 'chapter.nextChapter');
        previous = self.findInArray(url_json_content, 'chapter.previousChapter');
        sorted_images = sorted(images, key=lambda x: x['order']);
        # print(sorted_images)
        # print(next)

        img_element = lambda src: f'<img src="{src}"></img>'; 
        img_elements = map(lambda x: img_element(x['url']), sorted_images);
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));

        sections = self._url.split('/');
        story_type = self._configuration.get_story_type(body, sections);
        # img_selector = self._configuration.alt_selector or 'img';
        # byte_images = self._get_images_from_tags(img_tags=chapter.css(f'{img_selector}[{self._configuration.src}]' if not callable(self._configuration.src) else img_selector), src=self._configuration.src, img_selector=img_selector) if story_type == StoryType.MANGA else None;
        # if (byte_images is not None and len(byte_images) == 0 and story_type == StoryType.MANGA):
        #     print(body.html);
        return ScraperResult(
            story_type = story_type,
            urls = UrlResult(
                prev = "/".join(sections[:-1]) + '/' + previous['slug'] if previous else None,
                current = self._url,
                next = "/".join(sections[:-1]) + '/' + next['slug'] if next else None,
            ),
            chapter = chapter,
            lines = None,
            images = byte_images,
            titles = self._configuration.get_titles(body, sections),
            keys = self._configuration.get_keys(body, sections),
        )

    def findInArray(self, json_object, keys: str):
        if isinstance(json_object, collections.abc.Sequence) and len(json_object) > 0:
            keyList = keys.split('.')
            if not isinstance(json_object[0], str) and isinstance(json_object[0], collections.abc.Sequence):
                for child in json_object:
                    result = self.findInArray(child, keys);
                    if result: return result;
            else:
                obj = json_object[3]
                idx = 0
                stop = False
                while idx < len(keyList) and not stop:
                    key = keyList[idx];
                    # print(f'Look for {key}')
                    try:
                        if key in obj:
                            # print(f'Found {key}: {obj[key]}')
                            if len(keyList) - 1 == idx:
                                return obj[key];
                            obj = obj[key];
                            idx = idx + 1
                            continue;
                    except:
                        pass
                        # print(f'{key} not in {obj}')
                    stop = True
                    idx = idx + 1
                if 'children' in json_object[3]:
                    children = json_object[3]['children']
                    # print(children)
                
                    result = self.findInArray(json_object[3]['children'], keys);
                    if result: return result;
                
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            src = 'src',
            get_chapter = lambda node, sections: node.css_first('section > section'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4],
                chapter = sections[5],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        story = sections[4].split('-');
        chapter = sections[5].split('-');
        return KeyResult(
            chapter = " ".join(chapter).capitalize(),
            domain = None,
            story = " ".join(story).capitalize(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('a > button[aria-label="Previous"]');
        next = node.css_first('a > button[aria-label="Next"]');
        return UrlResult(
            prev = self.tryGetHref(prev),
            current = url,
            next = self.tryGetHref(next),
        );