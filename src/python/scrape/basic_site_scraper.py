import requests;
from selectolax.parser import HTMLParser, Node
from models.story_type import StoryType
from scrape.basic_scraper import BasicConfiguration;
from scrape.basic_scraper import BasicScraper, ScraperResult;
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

class BasicSiteScraper(BasicScraper):
    def __init__(self, url, driver=None, awaitTerm=None, session=None, configuration=None, headers={}):
        super().__init__(url, driver, session, headers);
        self.awaitTerm = awaitTerm;
        self._configuration: BasicConfiguration = configuration;
        self._handle(url, driver, session, headers);
        pass

    def _handle(self, url, driver, session, headers):
        parser = self._try_get_parser(url, driver, session, headers);
        if self._result is not None:
            return;
        self._result = self._scrape(parser)
        pass

    def _try_get_content(self, url:str, driver:WebDriver, session:requests.Session, headers={}):
        content = None;
        if driver is not None:
            if self.awaitTerm is None:
                driver.get(url)
                content = driver.page_source;
            else:
                driver.get(url)
                el = WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, self.awaitTerm))
                content = el.text;
        else:
            content = self._try_get_response(url, session, headers);
            if content is not None:
                content = content.content;
        return content;

    def _try_get_parser(self, url:str, driver:WebDriver, session:requests.Session, headers={}) -> Node:
        content = self._try_get_content(url, driver, session, headers)
        if self._result is not None:
            return;
        return HTMLParser(content).body;

    def _scrape(self, body: Node):
        if not self._configuration: raise Exception("Base Scraper needs a configuration")
        sections = self._url.split('/');
        chapter = self._configuration.get_chapter(body, sections);
        if chapter is None or not isinstance(chapter, Node):
            print('No chapter, check url', chapter)
            # print(body.html)
            return self._get_cannot_parse(self._url, not not self._driver);
        # print(body.html)
        buttons = self._configuration.get_buttons(body);
        story_type = self._configuration.get_story_type(body, sections);
        print(story_type);
        lines = BasicScraper.get_lines(chapter) if story_type == StoryType.NOVEL else None;

        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'), src=self._configuration.src) if story_type == StoryType.MANGA else None;
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(buttons),
            chapter = chapter,
            lines = lines,
            images = byte_images,
            title = self._configuration.get_title(body).text(),
            keys = self._configuration.get_keys(body, sections),
        )