from typing import Callable
import requests
from scrape.basic_scraper import BasicConfiguration, ScraperResult;
from helpers.driver import Driver
from selectolax.parser import Node;
from scrape.basic_site_scraper import BasicSiteScraper;

class ConfigureSiteScraper(BasicSiteScraper):
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0' };

    def getConfiguration(self, url: str) -> BasicConfiguration:
        raise NotImplementedError();

    def tryGetHref(self, element: Node, prefix='', check:Callable[[Node, str], bool]=lambda element, href: True):
        href = element and element.attributes.get('href');
        return prefix + href if href and (prefix != '' or href.startswith('http')) and check(element, href) else None;

    def useHtml(self, url: str, headers: dict[str, str]):
        super().__init__(url=url, configuration=self.getConfiguration(url), headers={**self.headers, **headers});

    def useReDriver(self, url: str, driver: Driver, headers: dict[str, str], awaitTerm: str|None = None):
        if driver.get_usage() > 0:
            conf = self.getConfiguration(url);
            self._result = ScraperResult._get_driver_requires_reset(url, conf.get_story_type(None, url.split('/')));
        else:
            self.useDriver(url, driver, headers, awaitTerm);

    def useDriver(self, url: str, driver: Driver, headers: dict[str, str], awaitTerm: str|None = None):
        conf = self.getConfiguration(url);
        if not driver.is_running():
            self._result = ScraperResult._get_driver_required(url, conf.get_story_type(None, url.split('/')));
        else:
            super().__init__(url=url, driver=driver.get(), awaitTerm=awaitTerm, configuration=conf, headers={**self.headers, **headers});

    def useSession(self, url: str, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        site_key = self.setupSession(url, session_dict, headers)
        super().__init__(url=url, session=session_dict.get(site_key), configuration=self.getConfiguration(url), headers={**self.headers, **headers});

        
    def setupSession(self, url: str, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        sections = url.split('/');
        base_url = "/".join(sections[:3]);
        domainSections = sections[2].split('.');
        if domainSections[0] == 'www':
            domainSections = domainSections[1:];
        site_key = '_'.join(domainSections);
        if not session_dict.get(site_key):
            session_dict[site_key] = requests.Session();
            session_dict[site_key].post(base_url, headers={**self.headers, **headers})
        return site_key;