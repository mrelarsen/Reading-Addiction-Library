import re
import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import HTMLParser, Node
from helpers.scraper_result import KeyResult, ScraperResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        # super().useHtml(url, headers);
        # super().useDriver(url, driver, headers);
        # super().useReDriver(url, driver, headers);;
        super().useSession(url, session_dict, headers);

    def _scrape(self, body: Node, head: Node, parser: HTMLParser):
        result = re.search(r'var chapImages = \'\S+\'', body.html or '');
        urls_finds = result.group() if result else '';
        sections = self._url.split('/');
        img_element = lambda src: f'<img src="{src}"></img>'; 
        img_elements = map(lambda x: img_element(x), urls_finds[len('var chapImages = \''):-1].split(','));
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
        story_type = self._configuration.get_story_type(body, sections);
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(body, sections),
            chapter = chapter,
            lines = None,
            images = byte_images,
            titles = self._configuration.get_titles(body, sections),
            keys = self._configuration.get_keys(body, sections),
        )
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            src = 'src',
            get_chapter = lambda node, sections: node.css_first('#chapter-images'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[3],
                chapter = sections[4],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        breadcrumb_items = node.css('#breadcrumbs-container .breadcrumbs-item span');
        print([x.text() for x in breadcrumb_items])
        return KeyResult(
            chapter = breadcrumb_items[1].text().strip(),
            domain = None,
            story = breadcrumb_items[0].text().strip(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://mangamonk.com';
        prev = node.css_first('.chapter__actions a#btn-prev');
        next = node.css_first('.chapter__actions a#btn-next');
        return UrlResult(
            prev = self.tryGetHref(prev, prefix, lambda node, href: self.isValidUrl(href)),
            current = url,
            next = self.tryGetHref(next, prefix, lambda node, href: self.isValidUrl(href)),
        );

    def isValidUrl(self, href:str):
        return len(href.split('/')) == 3;