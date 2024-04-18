import requests
from selectolax.parser import HTMLParser, Node
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.basic_file_scraper import BasicFileScraper, FileConfiguration;
from scrape.basic_scraper import ScraperResult, KeyResult, UrlResult;
import os;
import markdown;

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class FileScraper(BasicFileScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        super().__init__(url);

    def _try_read_file(self, path: str):
        html = '';
        with open(path, 'rb') as file:
            md_bytes = file.read();
            md = str(md_bytes, encoding='utf-8')
            html = markdown.markdown(md);
        return HTMLParser(html).body;

    def _scrape(self, body: Node):
        file_name, ext = os.path.splitext(self._url);
        return ScraperResult(
            story_type=get_story_type(None),
            urls = UrlResult(
                prev = None,
                current = f"file:///{self._url}",
                next = None,
            ),
            chapter = body,
            lines = ScraperResult.get_lines(body),
            titles = KeyResult(
                story = 'Markdown',
                chapter = file_name,
                domain=None,
            ),
            keys = KeyResult(
                story = None,
                chapter = None,
                domain = None,
            ),
        )
    
    def get_configuration(self) -> FileConfiguration:
        return None;