import importlib
import re
from types import ModuleType
import requests
import threading
import time;
from helpers.driver import Driver;
from queue import Queue
from scrape.basic_scraper import BasicScraper, ScraperResult;
from typing import Any

class WorkerTask():
    def __init__(self, url: str|None = None, urllist: list[str]|None = None, adjecent = False):
        url = url or (urllist and urllist[0]) or '';
        self.url = url if url == '' or url[0] != '!' else url[1:];
        self.urllist = urllist;
        self.adjecent = adjecent;
        self.tries = 0;
        pass

    def increment(self):
        self.tries += 1;
    
    def get_ensuing_task_from_list(self, dir: int, result: ScraperResult = None):
        if self.urllist and not result.is_loading():
            index, url = self.get_match(self.url);
            if url and (url[0] != '!' or dir < 0):
                next_index = dir + index;
                if index != -1 and next_index >= 0 and next_index < len(self.urllist):
                    return WorkerTask(self.urllist[next_index], self.urllist, True);
            elif dir > 0 and url:
                next = self.get_ensuing_url_from_result(dir, result);
                if next:
                    next_index, next_url = self.get_match(next);
                    if next_url:
                        self.urllist.remove(next_url);
                    self.urllist.insert(index + 1, '!' + next);
                    return WorkerTask(next, self.urllist, True);
                else:
                    if index + 1 < len(self.urllist):
                        return WorkerTask(self.urllist[index + 1], self.urllist, True);
        return None;

    def get_ensuing_url_from_result(self, dir: int, result: ScraperResult = None):
        if result:
            if dir < 0:
                return result.urls.prev;
            if dir == 0:
                return result.urls.current;
            if dir > 0:
                return result.urls.next;
        return None;

    def get_ensuing_task_from_result(self, dir: int, result: ScraperResult = None):
        url = self.get_ensuing_url_from_result(dir, result);
        if url:
            return WorkerTask(url, None, True);
        return None;

    def get_ensuing_task(self, dir: int, result: ScraperResult = None):
        task = self.get_ensuing_task_from_list(dir, result);
        return task or self.get_ensuing_task_from_result(dir, result);

    def get_match(self, url: str):
        if self.urllist:
            if url in self.urllist:
                index = self.urllist.index(url);
                return index, self.urllist[index];
            if f'!{url}' in self.urllist:
                index = self.urllist.index(f'!{url}');
                return index, self.urllist[index];
        return None, None;

class ScrapeHandler():
    def __init__(self, driver: Driver):
        self.queue: Queue = Queue(20);
        self.results: dict[str, ScraperResult] = {};
        self.loadings: dict[str, ScraperResult] = {};
        self.queueWorker = QueueWorker(self.queue, self.results, driver);
        pass

    def scrape(self, url:str|None = None, urllist: list[str]|None = None):
        task = WorkerTask(url, urllist);

        if task.url not in self.results:
            self.results[task.url] = ScraperResult._get_waiting(task.url, task.url);
            self.loadings[task.url] = self.results[task.url];
        elif task.url in self.loadings:
            self.loadings[task.url].updateLoading();

        if self.queue.maxsize * 0.5 > self.queue.qsize():
            self.queue.put(task);
        self.queueWorker.start_if_stopped();
        return self.results[task.url];

class QueueWorker():
    def __init__(self, queue: Queue[WorkerTask], results: dict[str, ScraperResult], driver: Driver):
        self.queue = queue;
        self.results = results;
        self.driver = driver;
        self.session_dict: dict[str, requests.Session] = {};
        self.modules: dict[str, ModuleType] = {};
        self.main_thread: threading.Thread|None = None;
        self.previous_url = None;
        self.a = 0;
        pass

    def start_if_stopped(self):
        if not self.main_thread or not self.main_thread.is_alive():
            self.main_thread = threading.Thread(target=self.run_tasks, daemon=False);
            self.main_thread.start();

    def run_tasks(self):
        while not self.queue.empty():
            task = self.queue.get();
            if task.url == self.previous_url:
                time.sleep(0.5)
            self.previous_url = task.url;
            self.run_task(task);

    def run_task(self, task: WorkerTask):
        if not task or not task.url:
            return;
    
        if not self.is_driver_ready(self.results[task.url]):
            if not self.driver.is_starting() and self.results[task.url].loading and self.results[task.url].counter == 1:
                print(f'start driver for task: {task.url}')
                self.driver.start_if_required(self.results[task.url], False);
                print(f'Driver started')
            if self.results[task.url].counter < 20:
                self.queue.put(task);
            return;

        modulename, alt_url = self.__get_module_name(task.url);
        if not modulename:
            print('Url format is not supported:', task.url);
            return False;

        url = alt_url or task.url;
        if self.results[task.url].is_loading():
            module: Any = self.__get_module(modulename);
            instance: BasicScraper = module(url, self.driver, self.session_dict);
            result: ScraperResult = instance.get_result(modulename);
            task.increment();
            if result.is_loading():
                if task.tries < 2: 
                    self.queue.put(task);
            else:
                print(f'url: {task and task.url}');
            self.results[task.url] = result;
        if not task.adjecent:
            self.add_task_if_missing(task, 1);
            self.add_task_if_missing(task, -1);
    
    def is_driver_ready(self, result: ScraperResult):
        if result.driver_required and not self.driver.is_running() or result.driver_requires_reset and self.driver.get_usage() > 0:
            return False;
        return True;

    
    def add_task_if_missing(self, task: WorkerTask, dir: int):
        next_task = task.get_ensuing_task(dir, self.results[task.url]);
        if next_task and next_task.url and next_task.url not in self.results:
            self.results[next_task.url] = ScraperResult._get_waiting(next_task.url, next_task.url);
            self.queue.put(next_task);

    def __get_module_name(self, scrape_url: str):
        if scrape_url.startswith("file"):
            url = scrape_url[8:];
            file_domain = re.split(r'[\\/]', scrape_url)[-1].split('__')[0];
            modulename = f"file_{file_domain}";
            return (modulename, url);
        elif scrape_url.startswith("http"):
            split_domain = scrape_url.split('/')[2].split('.');
            if 'www' in split_domain:
                split_domain.remove('www');
            modulename = "_".join(split_domain);
            return (modulename, None);
        return (None, None);

    def __get_module(self, modulename: str):
        if modulename in self.modules:
            return self.modules[modulename];
        modulename_path = self.__find_module(modulename)
        if modulename_path:
            module = importlib.import_module(modulename_path)
            site = getattr(module, 'SiteScraper') if hasattr(module, 'SiteScraper') else None;
            file = getattr(module, 'FileScraper') if hasattr(module, 'FileScraper') else None;
            module_class = site or file;
            if module_class:
                self.modules[modulename] = module_class;
                return module_class;
        return None;

    def __find_module(self, modulename: str):
        locations = ['scrape.sites', 'scrape.mangas', 'scrape.files'];
        for location in locations:
            domain_spec = importlib.util.find_spec(f'{location}.{modulename}')
            if domain_spec:
                return f'{location}.{modulename}';