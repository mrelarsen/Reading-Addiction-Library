import threading;
from os.path import exists
from typing import Optional
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from collections.abc import Callable
from scrape.basic_scraper import ScraperResult


class Driver():
    def __init__(self, call_javascript: Callable[[str, list], None]):
        self.__driver: WebDriver|None = None;
        self.__starting = False;
        self.__call_javascript = call_javascript;
        self.__usage = 0;

    def get(self):
        self.__usage += 1;
        return self.__driver;

    def get_usage(self):
        return self.__usage;

    def is_starting(self):
        return self.__starting;

    def is_running(self):
        return bool(not self.__starting and self.__driver);

    def reset(self, is_async = True, callback: Optional[Callable] = None):
        if self.__driver:
            self.__driver.quit();
        self.__driver = None;
        self.__usage = 0;
        self.toggle(True, is_async, callback);

    def toggle(self, on = True, is_async = True, callback: Optional[Callable] = None):
        if exists("../../libraries/geckodriver/geckodriver.exe") and on and not self.__driver and not self.__starting:
            self.__starting = True;
            if is_async:
                t = threading.Thread(target=self.__toggle_driver, args=(callback,), daemon=True);
                t.start();
            else:
                self.__toggle_driver(callback);
        elif not on and not self.__starting and self.__driver:
            self.__driver.quit();
            self.__driver = None;

    def __toggle_driver(self, callback: Optional[Callable] = None):
        self.__call_javascript('toggleLoadBar', [True]);
        firefox_options = webdriver.FirefoxOptions();
        if 'headless' in dir(firefox_options):
            firefox_options.headless = True;
        elif 'add_argument' in dir(firefox_options):
            firefox_options.add_argument("--headless");
        service = FirefoxService(executable_path="../../libraries/geckodriver/geckodriver.exe")
        self.__driver = webdriver.Firefox(service=service, options=firefox_options)
        self.__starting = False;
        self.__call_javascript('toggleLoadBar', [False]);
        if callback:
            callback();

    def start_if_required(self, result: ScraperResult, is_async = True, callback = None):
        if result.driver_required:
            if result.driver_requires_reset and (not self.is_running() or self.get_usage() > 0):
                self.reset(is_async, callback);
            else:
                self.toggle(True, is_async, callback);