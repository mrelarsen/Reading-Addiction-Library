from helpers.story_type import StoryType
from scrape.basic_scraper import ScraperResult
from helpers.driver import Driver
from scrape.basic_site_scraper import BasicSiteScraper;
import requests

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(BasicSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        self._url = url;
        self._result = ScraperResult._get_cannot_parse(self._url);