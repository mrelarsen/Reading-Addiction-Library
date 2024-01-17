import requests;
from models.story_type import StoryType
from models.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);
        
    def getConfiguration(self, url):
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.NOVEL,
            get_title = lambda node: node.css_first('h3'),
            get_chapter = lambda node, sections: self.clean_chapter(node.css('.entry-content .wp-block-columns .wp-block-column')[1]),
            get_buttons = lambda node: self.Object(
                prev = node.css('.entry-content .wp-block-columns .wp-block-column')[1].css('h3.has-text-align-center.wp-block-heading a')[0],
                next = node.css('.entry-content .wp-block-columns .wp-block-column')[1].css('h3.has-text-align-center.wp-block-heading a')[-1],
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev, '', lambda element: len(element.attributes.get('href').split('/')) == 6),
                current = url,
                next = self.tryGetHref(buttons.next, '', lambda element: len(element.attributes.get('href').split('/')) == 6),
            ),
            get_keys = lambda node, sections: self.Object(
                story = sections[3],
                chapter = sections[4],
            ),
        );

    def clean_chapter(self, node: Node):
        code_blocks = node.css('.code-block');
        for code_block in code_blocks:
            code_block.remove();
        return node;