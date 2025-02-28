import requests;
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
        # super().useReDriver(url, driver, headers);;
        super().useSession(url, session_dict, headers);
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            get_chapter = lambda node, sections: node.css_first('#htmlContent'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[3],
                chapter = sections[4],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h1')
        story = node.css_first('a#bookname')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = story.text(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://www.novelhall.com';
        prev = node.css_first('nav.nav-single a[rel="prev"]');
        next = node.css_first('nav.nav-single a[rel="next"]');
        return UrlResult(
            prev = self.tryGetHref(prev, prefix),
            current = url,
            next = self.tryGetHref(next, prefix),
        );