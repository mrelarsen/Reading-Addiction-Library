import re
from typing import Any
import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import Node, HTMLParser
from helpers.scraper_result import KeyResult, ScraperResult, UrlResult;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        super().useDriver(url, driver, '#readerarea');
        # super().useReDriver(url, driver);
        # super().useSession(url, session_dict);

    def _scrape(self, body: Node):
        urls_finds = re.findall(r'("https?://[^\s]+")', body.html);
        print(urls_finds)
        urls = [url[1:-1] for url in urls_finds if url.endswith('.jpg"') and 'lunarscan.org/wp-content/uploads' in url];
        urls = self.unique(urls)
        print(urls)
        if len(urls) == 0:
            print(body.html)
            return ScraperResult._get_error("No images were found", self._url);
        sections = self._url.split('/');
        img_element = lambda src: f'<img src="{src}"></img>'; 
        img_elements = map(lambda x: img_element(x), urls);
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
        story_type = self._configuration.get_story_type(body, sections);
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(body, sections),
            chapter = chapter,
            lines = None,
            images = byte_images,
            titles = self._configuration.get_titles(body, sections),
            keys = self._configuration.get_keys(body, sections),
        )
    
    def unique(self, list1: list[Any]):
        unique_list = [];
        for x in list1:
            if x not in unique_list:
                unique_list.append(x);
        return unique_list;
        
    def getConfiguration(self, url: str):
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.MANGA,
            src = 'src',
            get_chapter = lambda node, sections: node.css_first('#readerarea'),
            get_titles = lambda node, sections: self.get_titles(node, sections),
            get_urls = lambda node, sections: self.get_urls(node, sections, url),
            get_keys = lambda node, sections: self.Object(
                story = "-".join(sections[3].split('-')[:-2]),
                chapter = "-".join(sections[3].split('-')[-2:]),
                domain = None,
            ),
        );

    def get_titles(self, node: Node, sections: list[str]):
        chapter = node.css_first('h1.entry-title')
        return KeyResult(
            chapter = chapter.text(),
            domain = None,
            story = None,
        );

    def get_urls(self, node: Node, sections: list[str], url: str):
        prev = node.css_first('.nextprev a.ch-prev-btn');
        next = node.css_first('.nextprev a.ch-next-btn');
        return UrlResult(
                prev = self.tryGetHref(prev),
                current = url,
                next = self.tryGetHref(next),
        );