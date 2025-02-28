import requests;
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_scraper import ScraperResult;
from scrape.basic_site_scraper import BasicSiteScraper;
from selectolax.parser import HTMLParser
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class SiteScraper(BasicSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        super().__init__(url=url, headers=headers);

    def _run(self, a, b, c):
        self._result = self._scrape(None, None, None);
        
    def _scrape(self, _, __, ___):
        id = self._url.split('/')[3].split('-')[0]
        res = requests.get("https://www.wattpad.com/apiv2/info?id=" + id, headers={'User-Agent': 'Mozilla/5.0'})
        chapters = res.json()['group']
        chapter = [chapter for chapter in chapters if str(chapter['ID']) == str(id)][0];
        chapter_index = chapters.index(chapter);
        page = requests.get(f"https://www.wattpad.com/apiv2/storytext?id={id}", headers={'User-Agent': 'Mozilla/5.0'});
        if page.status_code != 200:
            return ScraperResult._get_default_tts(
                texts = ["Chapter not found!"],
                title = "Chapter not found!",
                url = self._url);

        body = HTMLParser(page.content).body;
        sections = self._url.split('/');
        print(res.json())
        return ScraperResult(
            story_type=get_story_type(sections),
            urls = UrlResult(
                prev = "https://www.wattpad.com/" + str(chapters[chapter_index - 1]['ID']) if 0 < chapter_index - 1 else None,
                current = self._url,
                next = "https://www.wattpad.com/" + str(chapters[chapter_index + 1]['ID']) if len(chapters) > chapter_index + 1 else None,
            ),
            chapter = body,
            lines = ScraperResult.get_lines(body),
            titles = KeyResult(
                chapter = chapter['TITLE'],
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                story = res.json()['group'],
                chapter = sections[3],
                domain = None,
            ),
        )