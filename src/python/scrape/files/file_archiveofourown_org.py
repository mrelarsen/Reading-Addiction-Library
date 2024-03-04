from helpers.story_type import StoryType
from scrape.basic_file_scraper import FileConfiguration
from helpers.driver import Driver
from scrape.basic_file_scraper import BasicFileScraper;
import requests;

class FileScraper(BasicFileScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        super().__init__(url);

    def get_configuration(self):
        return FileConfiguration(
            get_story_type=lambda x,y: StoryType.NOVEL,
            get_chapter=lambda body,id: body.css(f'#chapters .userstuff')[id-1],
            get_titles=lambda body: body.css('#chapters h2.heading'),
            get_keys=lambda body, id: self.Object(
                story = body.css('#preface .message a')[1].attributes['href'].split('/')[-1],
                chapter = id,
            )
        );