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
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.NOVEL,
            get_title = lambda node: node.css_first('.chapter-title'),
            get_chapter = lambda node, sections: node.css_first('#chp_contents #chp_raw'),
            get_buttons = lambda node: self.Object(
                prev = node.css_first('#chp_contents .nav_chp_fi .btn-prev'),
                next = node.css_first('#chp_contents .nav_chp_fi .btn-next'),
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev, check=lambda element: 'disabled' not in element.attributes.get('class')),
                current = url,
                next = self.tryGetHref(buttons.next, check=lambda element: 'disabled' not in element.attributes.get('class')),
            ),
            get_keys = lambda node, sections: self.Object(
                story = sections[4],
                chapter = sections[6],
            ),
        );