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
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: get_story_type(sections),
            get_chapter = lambda node, sections: node.css_first('.chapter-inner.chapter-content'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = '/'.join(sections[4:5]),
                chapter = '/'.join(sections[7:8]),
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h1')
        story = node.css_first('h2.inline-block')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = story.text(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://www.royalroad.com';
        prev = node.css('.portlet-body .row.nav-buttons .btn.btn-primary')[0];
        next = node.css('.portlet-body .row.nav-buttons .btn.btn-primary')[1];
        return UrlResult(
            prev = self.tryGetHref(prev, prefix, lambda element: element.tag == 'a'),
            current = url,
            next = self.tryGetHref(next, prefix, lambda element: element.tag == 'a'),
        );