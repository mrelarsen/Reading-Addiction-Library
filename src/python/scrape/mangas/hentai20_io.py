import requests
from models.story_type import StoryType
from models.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        # super().useSession(url, session_dict);

    def getConfiguration(self, url):
        prefix = 'https://hentai20.io';
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.MANGA,
            src = 'src',
            get_title = lambda node: node.css_first('ol.breadcrumb li a.active'),
            get_chapter = lambda node, sections: node.css_first('.reading-content'),
            get_buttons = lambda node: self.Object(
                prev = node.css_first('.nav-links .prev-page'),
                next = node.css_first('.nav-links .next-page'),
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev, prefix),
                current = url,
                next = self.tryGetHref(buttons.next, prefix),
            ),
            get_keys = lambda node, sections: self.Object(
                story = sections[4],
                chapter = sections[5],
            ),
        );