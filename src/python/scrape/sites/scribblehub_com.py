import requests;
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node, HTMLParser
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
            get_chapter = lambda node, sections: self.get_chapter(node),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: KeyResult(
                story = sections[4],
                chapter = sections[6],
                domain = None,
            ),
        );

    def get_chapter(self, node: Node):
        chapter = node.css_first('#chp_contents #chp_raw')
        # Needed for one story, might create problems in others
        spans = chapter.css('p span[lang="en-us"]');
        for span in spans:
            html_parser = HTMLParser(f'<span>{span.text(True, " ", True)}</span>')
            span.replace_with(html_parser.body.child)
        return chapter;

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('.chapter-title')
        story = node.css('.chp_byauthor > a')[0]
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = story.text(),
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('#chp_contents .nav_chp_fi .btn-prev');
        next = node.css_first('#chp_contents .nav_chp_fi .btn-next');
        return UrlResult(
            prev = self.tryGetHref(prev, check=lambda element, href: 'disabled' not in element.attributes.get('class')),
            current = url,
            next = self.tryGetHref(next, check=lambda element, href: 'disabled' not in element.attributes.get('class')),
        );