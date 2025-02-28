from types import ModuleType
import requests
import threading
import time;
from helpers.driver import Driver;
from queue import Queue
from helpers.worker_task import WorkerTask
from scrape.basic_scraper import BasicScraper, ScraperResult;

class ScrapeHandler():
    def __init__(self, driver: Driver, storyHeaders: dict[str, dict[str, str]]):
        self.queue: Queue = Queue(20);
        self.results: dict[str, ScraperResult] = {};
        self.queueWorker = QueueWorker(self.queue, self.results, storyHeaders, driver);
        pass

    def scrape(self, url:str|None = None, urllist: list[str]|None = None):
        task = WorkerTask.new(url, urllist);
        if not task: return;

        if task.url not in self.results:
            self.results[task.url] = ScraperResult._get_waiting(task.url, task.url, task.module_story_type);
        else:
            self.results[task.url].updateLoading(task.module_story_type);

        if self.queue.maxsize * 0.5 > self.queue.qsize():
            self.queue.put(task);
        self.queueWorker.start_if_stopped();
        return self.results[task.url];

class QueueWorker():
    def __init__(self, queue: Queue[WorkerTask], results: dict[str, ScraperResult], storyHeaders: dict[str, dict[str, str]], driver: Driver):
        self.queue = queue;
        self.results = results;
        self.storyHeaders = storyHeaders;
        self.driver = driver;
        self.session_dict: dict[str, requests.Session] = {};
        self.modules: dict[str, ModuleType] = {};
        self.main_thread: threading.Thread|None = None;
        self.previous_url = None;
        self.a = 0;
        pass

    def set_story_headers(self, story_headers: dict[str, dict[str, str]]):
        self.storyHeaders = story_headers;

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
            if not self.driver.is_starting() and self.results[task.url].loading and self.results[task.url].driver is None:
                print(f'start driver for task: {task.url}')
                self.results[task.url].driver = self.driver;
                self.driver.start_if_required(self.results[task.url], False);
                print(f'Driver started')
            if self.results[task.url].counter < 20 and self.queue.maxsize * 0.5 > self.queue.qsize():
                self.queue.put(task);
            return;

        if not task.module_name:
            print('Url format is not supported:', task.url);
            return False;

        url = task.alt_url or task.url;
        if self.results[task.url].is_loading():
            instance: BasicScraper = task.module_class(url, self.driver, self.session_dict, self.storyHeaders.get(task.module_name, {}));
            result: ScraperResult = instance.get_result(task.module_name);
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
            self.results[next_task.url] = ScraperResult._get_waiting_empty(next_task.url, next_task.url);
            self.queue.put(next_task);