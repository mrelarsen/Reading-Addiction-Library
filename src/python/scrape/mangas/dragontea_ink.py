from models.driver import Driver
from scrape.basic_site_scraper import BasicSiteScraper;
import requests

class SiteScraper(BasicSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        self._url = url;
        self._result = self._get_cannot_parse(self._url);