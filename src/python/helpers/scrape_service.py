from typing import Optional, Tuple
from helpers.async_scraper import ScrapeHandler
from helpers.reading_status import ReadingStatus
from helpers.story_type import StoryType
from helpers.driver import Driver
from helpers.worker_task import WorkerTask
from scrape.basic_scraper import ScraperResult
from database.history import History   
    
class ScrapeService():
    def __init__(self, history: History, driver: Driver, storyHeaders: dict[str, dict[str, str]]):
        self.history = history;
        self.driver = driver;
        self.async_scraper = ScrapeHandler(driver, storyHeaders);
        self.result: ScraperResult = None;
        self.urllist: Optional[list[str]] = None;

    def read_info(self, url: Optional[str] = None, dir: int = 0, urllist: Optional[list[str]] = None, buffer = True, loading = True) -> Tuple[StoryType, ScraperResult]:
        urllist = self.urllist if not urllist and self.urllist and (dir and (self.get_urls()[dir+1] in self.urllist or f'!{self.get_urls()[dir+1]}' in self.urllist)) else urllist;
        result = None;
        if self.result and not url and urllist == self.urllist:
            result = self.__scrape(self.get_urls()[dir+1], urllist);
        elif urllist and len(urllist) > 1:
            result = self.__scrape(urllist=urllist);
        elif url or (urllist and len(urllist) == 1):
            result = self.__scrape(url or urllist and urllist[0] or '');
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

    def __scrape(self, url: Optional[str] = None, urllist: Optional[list[str]] = None) -> ScraperResult:
        self.urllist = urllist;
        if url or urllist and urllist[0]:
            return self.async_scraper.scrape(url=url, urllist=urllist);

    def get_story(self):
        if self.result and self.result.keys:
            return (self.history.get_story(None, self.result.keys.story, self.result.keys.domain), self.result.keys.story);
        return (None, None);

    def try_to_save(self, status = ReadingStatus.COMPLETED):
        if self.history and self.result and self.result.keys and self.result.keys.story and self.result.keys.chapter and self.result.keys.domain:
            return self.history.add_chapter(self.result, status);
        return None;
        
    def get_urls(self):
        if self.result is None: return self.get_empty_urls();
        task = WorkerTask.new(self.result.urls.current, self.urllist);
        if task is None: return self.get_empty_urls();
        next_task = task.get_ensuing_task(1, self.result)
        prev_task = task.get_ensuing_task(-1, self.result)
        return [
            prev_task and prev_task.url,
            self.result.urls.current,
            next_task and next_task.url,
            self.urllist,
        ];

    def get_empty_urls(self):
        return [
            None,
            None,
            None,
            self.urllist,
        ];
