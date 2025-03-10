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
            get_chapter = lambda node, sections: self.clean_chapter(node.css('.entry-content .wp-block-columns .wp-block-column')[1]),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[3],
                chapter = sections[4],
                domain = None,
            ),
        );

    def clean_chapter(self, node: Node):
        code_blocks = node.css('.code-block');
        for code_block in code_blocks:
            code_block.remove();
        return node;

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h3')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css('.entry-content .wp-block-columns .wp-block-column')[1].css('h3.has-text-align-center.wp-block-heading a')[0];
        next = node.css('.entry-content .wp-block-columns .wp-block-column')[1].css('h3.has-text-align-center.wp-block-heading a')[-1];
        return UrlResult(
            prev = self.tryGetHref(prev, '', lambda element, href: len(href.split('/')) == 6),
            current = url,
            next = self.tryGetHref(next, '', lambda element, href: len(href.split('/')) == 6),
        );