import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        # super().useHtml(url, headers);
        # super().useDriver(url, driver, headers);
        super().useReDriver(url, driver, headers);
        # super().useSession(url, session_dict, headers);

    def getConfiguration(self, url: str) -> BasicConfiguration:
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            get_chapter = lambda node, sections: node.css_first('.entry-content'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4],
                chapter = sections[5],
                domain = None,
            )
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('ol.breadcrumb li.active')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('.nav-previous a.prev_page')
        next = node.css_first('.nav-next a.next_page')
        return UrlResult(
            prev = self.tryGetHref(prev),
            current = url,
            next = self.tryGetHref(next),
        );