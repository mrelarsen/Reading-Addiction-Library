import codecs
from typing import Any, Callable, Optional;
from selectolax.parser import HTMLParser, Node
from models.story_type import StoryType;
from scrape.basic_scraper import BasicScraper, ScraperResult;

class FileConfiguration():
    def __init__(self, get_story_type: Callable[[Node, list[str]], StoryType], get_titles: Callable[[Node], Node], get_keys: Callable[[Node, int], Any], get_chapter: Optional[Callable[[Node, int], Node]] = None, src: Optional[str] =None):
        self.get_story_type = get_story_type;
        self.src = src;
        self.get_chapter = get_chapter;
        self.get_titles = get_titles;
        self.get_keys = get_keys;
        pass

class BasicFileScraper(BasicScraper):
    def __init__(self, url):
        super().__init__(url);
        self._configuration = self.get_configuration();
        try:
            body = self._try_read_file(url);
            self._result = self._scrape(body);
        except Exception as error:
            self._result = self._get_error(error, self._url);
        pass

    def _try_read_file(self, path):
        page = None;
        path = "#".join(path.split('#')[:-1])
        with codecs.open(path, 'r', 'utf-8') as f:
            page = f.read();
        return HTMLParser(page).body;

    def _scrape(self, body: Node):
        id = int(self._url.split('_')[-1]);
        chapter = self._configuration.get_chapter(body, id);
        chapter_titles = self._configuration.get_titles(body);
        keys = self._configuration.get_keys(body, self._url.split('/'));
        return ScraperResult(
            story_type=self._configuration.get_story_type(body, self._url.split('/')),
            urls = self.Object(
                prev = f"file:///{'_'.join(self._url.split('_')[:-1])}_{id-1}" if id > 1 else None,
                current = f"file:///{self._url}",
                next = f"file:///{'_'.join(self._url.split('_')[:-1])}_{id+1}" if len(chapter_titles) > id else None,
            ),
            chapter = chapter,
            lines = BasicScraper.get_lines(chapter),
            title = chapter_titles[id - 1].text(),
            keys = self.Object(
                story = keys.story,
                chapter = keys.chapter,
            ),
        )
    
    def get_configuration(self) -> FileConfiguration:
        raise NotImplementedError();