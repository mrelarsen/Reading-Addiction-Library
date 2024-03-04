import requests;
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node
from helpers.scraper_result import KeyResult, UrlResult;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        # super().useSession(url, session_dict);
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.NOVEL,
            get_chapter = lambda node, sections: node.css_first('.post-content .par'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[3],
                chapter = sections[4],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('.current-crumb')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('.chapter-nav .prev');
        next = node.css_first('.chapter-nav .next');
        return UrlResult(
            prev = self.tryGetHref(prev),
            current = url,
            next = self.tryGetHref(next),
        );