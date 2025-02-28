import re
from typing import Any
import requests
from selectolax.parser import HTMLParser
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.configure_site_scraper import ConfigureSiteScraper;
from requests import Session
from scrape.basic_scraper import BasicScraper, ScraperResult;
from selenium.webdriver.remote.webdriver import WebDriver
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, Session], headers: dict[str, str]):
        # self.useHtml(url);
        self.useSession(url, session_dict, headers);
        
    def _handle(self, url: str, driver: WebDriver, session: requests.Session, headers: Any):
        try:
            sections = url.split('/')
            story_id = sections[4].split('_')[-1];
            chapter_id = sections[5].split('_')[-1];
            if len(sections) < 7:
                super()._try_get_content(url, driver, session, headers);
                cookies_dict = session.cookies.get_dict();
                _csrfToken = cookies_dict['_csrfToken'];
                print(_csrfToken)
            if len(sections) < 7 and not _csrfToken:
                self._result = ScraperResult._get_error('No token was given or found, add "/<token>" to the url manually', self._url);
                return;
            token = len(sections) > 6 and sections[6] or _csrfToken;
            json: dict = super()._try_get_json(f'https://webnovel.com/go/pcm/chapter/getContent?csrfToken={token}&_fase=0&bookId={story_id}&chapterId={chapter_id}&encryptType=3&font=Merriweather&_=1676760223402', session, headers);
            if not json:
                return;
            if not self.walk(json, 'data.chapterInfo.contents.0.content'):
                self._result = ScraperResult._get_error(f'Token {token} did not work in retrieving the content of the chapter, add another token manually by adding /*token* to the url e.g. {"/".join(sections[:6])}/{token}', self._url);
                return;
            chapterInfo: dict[str, Any] = self.walk(json, 'data.chapterInfo');
            contents: list[dict]|None = chapterInfo.get('contents');
            if not contents:
                self._result = ScraperResult._get_error('Could not retrieve contents', self._url);
                return;
            htmlStr = "".join([f'<div>{x["content"]}</div>' for x in contents if x.get("content") is not None]);
            chapter = HTMLParser(htmlStr).body;
            lines = ScraperResult.get_lines(chapter);
            self._result = ScraperResult(
                story_type = get_story_type(sections),
                urls = UrlResult(
                    prev = None if chapterInfo.get('preChapterId') == '-1' else self.getUrl(sections, chapterInfo['preChapterId'], chapterInfo['preChapterName'], token),
                    current = url,
                    next = None if chapterInfo.get('nextChapterId') == '-1' else self.getUrl(sections, chapterInfo['nextChapterId'], chapterInfo['nextChapterName'], token)
                ),
                chapter = chapter,
                lines = lines,
                titles = KeyResult(
                    chapter = chapterInfo.get('chapterName'),
                    domain = None,
                    story = None,
                ),
                keys = KeyResult(
                    story = story_id,
                    chapter = chapter_id,
                    domain = None,
                ),
            )
        except Exception as error:
            self._result = ScraperResult._get_error(error, self._url);
        pass
    
    def walk(self, dict: dict, path: str):
        routes = path.split('.');
        result = dict;
        for route in routes:
            if route.isdigit():
                index = int(route);
                if len(result) <= index:
                    print(f'Cannot read index: {index}/{len(result)}, on {result}');
                    return None;
                result = result[index];
                continue;
            if route not in result:
                print(f'Cannot walk path: {path}, beyond {route}, on {result}');
                return None;
            result = result[route];
        return result;

    def getUrl(self, sections: list[str], chapterId: int, chapterName: str, token: str):
        prefix = "/".join(sections[:5]);
        chapter = "-".join(re.split(r'[\s/]', chapterName.lower()));
        return f'{prefix}/{chapter}_{chapterId}/{token}';

    def getConfiguration(self, url: str):
        return None;