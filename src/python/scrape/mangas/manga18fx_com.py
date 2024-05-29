import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver, '.read-content');
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);
        
    def getConfiguration(self, url: str):
        prefix = 'https://manga18fx.com';
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            src = 'data-src',
            get_chapter = lambda node, sections: node.css_first('.read-content'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4],
                chapter = sections[5],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('ol.breadcrumb li a.active')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://manga18fx.com';
        prev = node.css_first('a.navi-change-chapter-btn-prev');
        next = node.css_first('a.navi-change-chapter-btn-next');
        return UrlResult(
            prev = self.tryGetHref(prev, prefix),
            current = url,
            next = self.tryGetHref(next, prefix),
        );