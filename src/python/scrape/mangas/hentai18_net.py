import requests
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
            get_story_type = lambda node, sections: StoryType.MANGA,
            src = 'data-original',
            get_chapter = lambda node, sections: node.css_first('.chapter-content'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = node.css_first('h1.chapter-title a').attributes['href'].split('/')[2],
                chapter = sections[4][len(node.css_first('h1.chapter-title a').attributes['href'].split('/')[2])+1:],
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h1.chapter-title')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prefix = 'https://hentai18.net';
        prev = node.css_first('.chapter-nav .btn-chapter-prev');
        next = node.css_first('.chapter-nav .btn-chapter-next');
        return UrlResult(
                prev = self.tryGetHref(prev, prefix),
                current = url,
                next = self.tryGetHref(next, prefix),
        );