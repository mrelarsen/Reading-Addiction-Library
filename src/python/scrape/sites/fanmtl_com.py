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
            get_chapter = lambda node, sections: self.get_chapter(node, sections),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4].split('_')[0],
                chapter = sections[4].split('_')[1],
                domain = None,
            ),
        );

    def get_chapter(self, node: Node, sections):
        content = node.css_first('.chapter-content');
        return content;

    def get_titles(self, node: Node, sections: list[str]):
        story = node.css_first('div.titles h1');
        chapter = node.css_first('div.titles h2');
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = story.text(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://www.fanmtl.com'
        prev = node.css_first('.action-select a.chnav.prev:not(.isDisabled)');
        next = node.css_first('.action-select a.chnav.next:not(.isDisabled)');
        return UrlResult(
            prev = self.tryGetHref(prev, prefix),
            current = url,
            next = self.tryGetHref(next, prefix),
        );