from typing import Callable
import requests;
from models.driver import Driver
from selectolax.parser import Node;
from scrape.basic_site_scraper import BasicSiteScraper;

class ConfigureSiteScraper(BasicSiteScraper):
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0' };

    def getConfiguration(self, url):
        raise NotImplementedError();

    def tryGetHref(self, element: Node, prefix='', check:Callable[[Node], bool]=lambda element: True):
        href = element and element.attributes.get('href');
        return prefix + href if check(element) and href and (prefix != '' or href.startswith('http')) else None;

    def useHtml(self, url):
        super().__init__(url=url, configuration=self.getConfiguration(url), headers=self.headers);

    def useReDriver(self, url, driver: Driver):
        if driver.get_usage() > 0:
            self._result = self._get_driver_requires_reset(url);
        else:
            self.useDriver(url, driver);

    def useDriver(self, url, driver: Driver):
        if not driver.is_running():
            self._result = self._get_driver_required(url);
        else:
            super().__init__(url=url, driver=driver.get(), configuration=self.getConfiguration(url), headers=self.headers);

    def useSession(self, url, session_dict: dict[str, requests.Session]):
        sections = url.split('/');
        base_url = "/".join(sections[:3]);
        domainSections = sections[2].split('.');
        if domainSections[0] == 'www':
            domainSections = domainSections[1:];
        site_key = '_'.join(domainSections);
        if not session_dict.get(site_key):
            session_dict[site_key] = requests.Session();
            session_dict[site_key].post(base_url, headers=self.headers)
        super().__init__(url=url, session=session_dict.get(site_key), configuration=self.getConfiguration(url), headers=self.headers);