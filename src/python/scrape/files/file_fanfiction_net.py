from helpers.story_type import StoryType
from scrape.basic_file_scraper import FileConfiguration
from helpers.driver import Driver
from scrape.basic_file_scraper import BasicFileScraper;
import requests;

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class FileScraper(BasicFileScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        super().__init__(url);

    def get_configuration(self):
        return FileConfiguration(
            get_story_type=lambda node, sections: get_story_type(sections),
            get_chapter=lambda body,id: body.css_first(f'#chap_{id}'),
            get_keys=lambda body,id: self.Object(
                story = body.css_first('a[rel]').attributes['href'].split('/')[4],
                chapter = id,
            ),
            get_titles=lambda body: body.css('#contents-list a'),
            get_story_title=lambda body: body.css_first('h1 .title'),
        );