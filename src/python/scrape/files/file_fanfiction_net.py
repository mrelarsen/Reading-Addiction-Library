from models.story_type import StoryType
from scrape.basic_file_scraper import FileConfiguration
from models.driver import Driver
from scrape.basic_file_scraper import BasicFileScraper;
import requests;

class FileScraper(BasicFileScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        super().__init__(url);

    def get_configuration(self):
        return FileConfiguration(
            get_story_type=lambda x,y: StoryType.NOVEL,
            get_chapter=lambda body,id: body.css_first(f'#chap_{id}'),
            get_keys=lambda body,id: self.Object(
                story = body.css_first('a[rel]').attributes['href'].split('/')[4],
                chapter = id,
            ),
            get_titles=lambda body: body.css('#contents-list a'),
        );