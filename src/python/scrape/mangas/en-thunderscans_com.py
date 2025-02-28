import json
import re
import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from selectolax.parser import Node, HTMLParser
from helpers.scraper_result import KeyResult, ScraperResult, UrlResult;
from scrape.mangas.asuracomic_net import SiteScraper as Asuratoon;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(Asuratoon):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        # super().useHtml(url, headers);
        super().useDriver(url, driver, headers, '#readerarea');
        # super().useReDriver(url, driver, headers);;
        # super().useSession(url, session_dict, headers);

    def _scrape(self, body: Node, head: Node, parser: HTMLParser):
        if not self._configuration: raise Exception("Base Scraper needs a configuration")
        sections = self._url.split('/');
        chapter = self._configuration.get_chapter(body, sections);
        if chapter is None or not isinstance(chapter, Node):
            print('No chapter, check url', self._url, chapter)
            print(body.html)
            return ScraperResult._get_cannot_parse(self._url, not not self._driver);
        # print(body.html)
        result = re.search(r'ts_reader.run\(.+\);', body.html or '');
        jsonStr = result.group() if result else '';
        # print(jsonStr[len('ts_reader.run('): -len(');')])
        jsonObj = json.loads(jsonStr[len('ts_reader.run('): -len(');')]);
        story_type = self._configuration.get_story_type(body, sections);
        lines = ScraperResult.get_lines(chapter) if story_type == StoryType.NOVEL else None;
        byte_images = self._get_images_from_tags(img_tags=chapter.css(f'img[{self._configuration.src}]' if not callable(self._configuration.src) else 'img'), src=self._configuration.src) if story_type == StoryType.MANGA else None;
        return ScraperResult(
            story_type = story_type,
            urls = UrlResult(
                prev = jsonObj.get('prevUrl'),
                current = self._url,
                next = jsonObj.get('nextUrl'),
            ),
            chapter = chapter,
            lines = lines,
            images = byte_images,
            titles = self._configuration.get_titles(body, sections),
            keys = self._configuration.get_keys(body, sections),
        );
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            src = 'src',
            get_chapter = lambda node, sections: node.css_first('#readerarea'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = "-".join(sections[3].split('-')[:-2]),
                chapter = "-".join(sections[3].split('-')[-2:]),
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h1.entry-title')
        story = node.css_first('.headpost .allc a')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = story.text(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('.nextprev a.ch-prev-btn');
        next = node.css_first('.nextprev a.ch-next-btn');
        return UrlResult(
            prev = self.tryGetHref(prev),
            current = url,
            next = self.tryGetHref(next),
        );