import importlib
import re
import requests
import threading
import time;
from models.driver import Driver;
from queue import Queue
from scrape.basic_scraper import BasicScraper, ScraperResult;
from typing import Any

class WorkerTask():
    def __init__(self, url:str=None, urllist:list[str]=None, adjecent=False):
        self.url = url or (urllist and urllist[0]);
        self.urllist = urllist;
        self.adjecent = adjecent;
        self.tries = 0;
        pass

    def increment(self):
        self.tries += 1;

    def get_ensuing_task(self, dir, result:ScraperResult=None):
        if self.urllist and self.url in self.urllist and not result.is_loading():
            index = self.urllist.index(self.url);
            next_index = dir + index;
            if index != -1 and next_index >= 0 and next_index < len(self.urllist):
                return WorkerTask(self.urllist[next_index], self.urllist, True);
            return None;
        if result:
            if dir == -1:
                return WorkerTask(result.urls.prev, None, True);
            if dir == 1:
                return WorkerTask(result.urls.next, None, True);
        return None;

class ScrapeHandler():
    def __init__(self, driver: Driver):
        self.queue = Queue(20);
        self.results: dict[str, ScraperResult] = {};
        self.loadings: dict[str, ScraperResult] = {};
        self.queueWorker = QueueWorker(self.queue, self.results, driver);
        pass

    def scrape(self, url=None, urllist=None):
        task = WorkerTask(url, urllist);

        if task.url not in self.results:
            self.results[task.url] = BasicScraper._get_waiting(task.url, task.url);
            self.loadings[task.url] = self.results[task.url];
        elif task.url in self.loadings:
            print ('redo loading')
            loading = BasicScraper._get_waiting(task.url, task.url);
            self.loadings[task.url].chapter = loading.chapter,
            self.loadings[task.url].lines = loading.lines,
            self.loadings[task.url].counter += 1;
            print(self.results[task.url].counter)

        if self.queue.maxsize * 0.5 > self.queue.qsize():
            self.queue.put(task);
        self.queueWorker.start_if_stopped();
        return self.results[task.url];

class QueueWorker():
    def __init__(self, queue, results, driver):
        self.queue: Queue[WorkerTask] = queue;
        self.results: dict[str, ScraperResult] = results;
        self.driver: Driver = driver;
        self.session_dict: dict[str, requests.Session] = {};
        self.modules = {};
        self.main_thread: threading.Thread = None;
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
            self.results[next_task.url] = BasicScraper._get_waiting(next_task.url, next_task.url);
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

    def __get_module(self, modulename):
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

    def __find_module(self, modulename):
        locations = ['scrape.sites', 'scrape.mangas', 'scrape.files'];
        for location in locations:
            domain_spec = importlib.util.find_spec(f'{location}.{modulename}')
            if domain_spec:
                return f'{location}.{modulename}';