import codecs
import requests;
from selectolax.parser import HTMLParser, Node
from helpers.story_type import StoryType
from scrape.basic_scraper import BasicConfiguration;
from scrape.basic_scraper import BasicScraper, ScraperResult;
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class BasicSiteScraper(BasicScraper):
    def __init__(self, url: str, driver: WebDriver|None = None, awaitTerm: str|None = None, session: requests.Session|None = None, configuration: BasicConfiguration = None, headers = {}):
        super().__init__(url, driver, session, headers);
        self.awaitTerm = awaitTerm;
        self._configuration = configuration;
        self._handle(url, driver, session, headers);
        pass

    def _handle(self, url: str, driver: WebDriver|None, session: requests.Session|None, headers: dict):
        parser = self._try_get_parser(url, driver, session, headers);
        if self._result is not None:
            return;
        self._result = self._scrape(parser)
        pass

    def _try_get_content(self, url: str, driver: WebDriver|None, session: requests.Session|None, headers={}):
        content = None;
        if driver is not None:
            if self.awaitTerm is None:
                driver.get(url)
                content = driver.page_source;
            else:
                driver.get(url)
                el = None;
                try:
                    el = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, self.awaitTerm))
                except TimeoutException:
                    print('Timed out after 10 seconds')
                    pass
                while el is not None and next((x for x in dir(el) if x == 'parent'), None) and el.parent is not None and el.tag_name != 'body':
                    el = el.parent;
                content = el and el.page_source or driver.page_source;
        else:
            response = self._try_get_response(url, session, headers);
            if response is not None:
                content = response.content;
        return content;

    def try_to_decode(self, content: bytes):
        string = 'None';
        for encoding in ['uft-8', 'latin-1', 'ascii', 'unicode']:
            try:
                string = codecs.encode(codecs.decode(content, encoding), 'utf-8');
                print(encoding)
            except:
                continue;
        return string;

    def _try_get_parser(self, url:str, driver:WebDriver|None, session:requests.Session|None, headers={}) -> Node:
        content = self._try_get_content(url, driver, session, headers)
        if self._result is not None:
            return;
        return HTMLParser(content).body;

    def _scrape(self, body: Node):
        if not self._configuration: raise Exception("Base Scraper needs a configuration")
        sections = self._url.split('/');
        chapter = self._configuration.get_chapter(body, sections);
        if chapter is None or not isinstance(chapter, Node):
            print('No chapter, check url', self._url, chapter)
            print(body.html)
            return ScraperResult._get_cannot_parse(self._url, not not self._driver);
        # print(body.html)
        story_type = self._configuration.get_story_type(body, sections);
        print(story_type);
        lines = ScraperResult.get_lines(chapter) if story_type == StoryType.NOVEL else None;

        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'), src=self._configuration.src) if story_type == StoryType.MANGA else None;
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(body, sections),
            chapter = chapter,
            lines = lines,
            images = byte_images,
            titles = self._configuration.get_titles(body, sections),
            keys = self._configuration.get_keys(body, sections),
        )