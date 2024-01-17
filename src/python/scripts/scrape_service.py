from typing import Tuple
from scripts.async_scraper import WorkerTask, ScrapeHandler
from models.reading_status import ReadingStatus
from models.story_type import StoryType
from models.driver import Driver
from scrape.basic_scraper import ScraperResult
from database.history import History   
    
class ScrapeService():
    def __init__(self, history: History, driver: Driver):
        self.history = history;
        self.driver = driver;
        self.async_scraper = ScrapeHandler(driver);
        self.result = None;
        self.urllist: list[str] = None;

    def read_info(self, url = None, dir = 0, urllist = None, buffer = True, loading = True) -> Tuple[StoryType, ScraperResult]:
        urllist = self.urllist if not urllist and self.urllist and (dir and self.get_urls()[dir+1] in self.urllist) else urllist;
        result = None;
        if self.result and not url and urllist == self.urllist:
            result = self.__scrape(self.get_urls()[dir+1], urllist);
        elif urllist and len(urllist) > 1:
            result = self.__scrape(urllist=urllist);
        elif url or (urllist and len(urllist) == 1):
            result = self.__scrape(url or urllist[0]);
        if result:
            self.result = result;
            story_type = self.result.story_type;
            if story_type == StoryType.NOVEL:
                return (StoryType.NOVEL, self.result)
            elif story_type == StoryType.MANGA:
                return (StoryType.MANGA, self.result)
        else:
            print('Url not found or wrong format!');
        return (None, None);

    def __scrape(self, url=None, urllist:list[str]=None) -> ScraperResult:
        self.urllist = urllist;
        if url or urllist and urllist[0]:
            return self.async_scraper.scrape(url=url, urllist=urllist);

    def get_story(self):
        if self.result and self.result.keys.story and self.result.domain:
            return (self.history.get_story(None, self.result.keys.story, self.result.domain), self.result.keys.story);
        return (None, None);

    def try_to_save(self, status=ReadingStatus.COMPLETED):
        if self.history and self.result and self.result.keys and self.result.keys.story and self.result.keys.chapter and self.result.domain:
            return self.history.add_chapter(self.result.urls.current, self.result, self.result.domain, status);
        return None;
        
    def get_urls(self):
        task = self.result and WorkerTask(self.result.urls.current, self.urllist);
        next_task = self.result and task.get_ensuing_task(1, self.result)
        prev_task = self.result and task.get_ensuing_task(-1, self.result)
        return [
            prev_task and prev_task.url,
            self.result and self.result.urls.current,
            next_task and next_task.url,
            self.urllist,
        ];
