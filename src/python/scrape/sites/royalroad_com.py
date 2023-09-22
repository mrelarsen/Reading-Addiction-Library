import requests;
from models.story_type import StoryType
from models.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);
        
    def getConfiguration(self, url):
        prefix = 'https://www.royalroad.com';
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.NOVEL,
            get_title = lambda node: node.css_first('h1'),
            get_chapter = lambda node, sections: node.css_first('.chapter-inner.chapter-content'),
            get_buttons = lambda node: self.Object(
                prev = node.css('.portlet-body .row.nav-buttons .btn.btn-primary')[0],
                next = node.css('.portlet-body .row.nav-buttons .btn.btn-primary')[1],
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev, prefix, lambda element: element.tag == 'a'),
                current = url,
                next = self.tryGetHref(buttons.next, prefix, lambda element: element.tag == 'a'),
            ),
            get_keys = lambda node, sections: self.Object(
                story = '/'.join(sections[4:5]),
                chapter = '/'.join(sections[7:8]),
            ),
        );