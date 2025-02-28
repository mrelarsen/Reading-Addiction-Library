import requests
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
        super().useDriver(url, driver, headers, '#readerarea');
        # super().useReDriver(url, driver, headers);
        # super().useSession(url, session_dict, self.headers);

    def _scrape(self, body: Node, head: Node, parser: HTMLParser):
        if not self._configuration: raise Exception("Base Scraper needs a configuration")
        sections = self._url.split('/');
        chapter = self._configuration.get_chapter(body, sections);
        if chapter is None or not isinstance(chapter, Node):
            print('No chapter, check url', self._url, chapter)
            print(body.html)
            return ScraperResult._get_cannot_parse(self._url, not not self._driver);
        # print(body.html)

        story_type = self._configuration.get_story_type(body, sections);
        lines = ScraperResult.get_lines(chapter) if story_type == StoryType.NOVEL else None;
        byte_images = self._get_images_from_tags(img_tags=chapter.css(f'img[{self._configuration.src}][alt*="chapter"]' if not callable(self._configuration.src) else 'img'), src=self._configuration.src) if story_type == StoryType.MANGA else None;
        if (not lines or len(lines) == 0) and (not byte_images or len(byte_images) == 0):
            print('No lines or image matches', self._url, chapter)
            print(body.html);
            return ScraperResult._get_cannot_parse(self._url, not not self._driver);
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(chapter, sections),
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
            get_chapter = lambda node, sections: node.css_first('body'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4],
                chapter = sections[6],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('button > h2')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        parent = node.css_first('.gap-x-3');
        hrefs = parent.css('a');
        prev, next = self.getPrevNext(hrefs);
        prefix = 'https://asuracomic.net'
        return UrlResult(
            prev = self.tryGetHref(prev, prefix),
            current = url,
            next = self.tryGetHref(next, prefix),
        );

    def getPrevNext(self, nodes: list[Node]):
        prev = None;
        next = None;
        for node in nodes:
            prevNode = node.css_first('svg.lucide-chevron-left');
            if (prevNode): prev = node;
            nextNode = node.css_first('svg.lucide-chevron-right');
            if (nextNode): next = node;
        return prev, next;