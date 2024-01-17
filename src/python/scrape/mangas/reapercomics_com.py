import requests
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
            get_story_type = lambda node, sections: { 'comics': StoryType.MANGA, 'novels': StoryType.NOVEL }[sections[3]],
            src = 'src',
            get_title = lambda node: node.css_first('main nav div.hidden'),
            get_chapter = lambda node, sections: { 'comics': node.css_first('main'), 'novels': node.css_first('main article') }[sections[3]],
            get_buttons = lambda node: self.Object(
                prev = node.css_first('main nav div.flex:not(.justify-end) a'),
                next = node.css('main nav div.flex.justify-end a')[1] if len(node.css('main nav div.flex.justify-end a')) > 2 else None,
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev),
                current = url,
                next = self.tryGetHref(buttons.next),
            ),
            get_keys = lambda node, sections: self.Object(
                story = sections[4],
                chapter = sections[6],
            ),
        );