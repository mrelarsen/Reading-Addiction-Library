import requests
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.configure_site_scraper import ConfigureSiteScraper;
from selectolax.parser import HTMLParser
from helpers.scraper_result import KeyResult, ScraperResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        # super().useHtml(url, headers);
        # super().useDriver(url, driver, headers);
        # super().useReDriver(url, driver, headers);;
        # super().useSession(url, session_dict, headers);
        self._url = url;
        self._headers = {**self.headers, **headers};
        self._session = None;
        sections = url.split(':')
        memes = [];
        subreddits = sections[1:];
        if len(subreddits) == 0:
            meme_content = self._try_get_json('https://meme-api.com/gimme/20', None, self.headers);
            memes = meme_content.get('memes');
        else:
            for subreddit in subreddits:
                meme_content = self._try_get_json(f'https://meme-api.com/gimme/{subreddit}/10', None, self.headers);
                memes = memes + meme_content.get('memes');
        img_element = lambda src: f'<img src="{src}"></img>'; 
        img_elements = [img_element(x.get('url')) for x in memes];
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
        byte_images = [[x, None] for x in byte_images];
        byte_images = [x for xs in byte_images for x in xs];

        print('meme chapter', chapter)
        self._result = ScraperResult(
            story_type = get_story_type(sections),
            urls = UrlResult(
                prev = None,
                current = url,
                next = url if sections[0][0] == '!' else None,
            ),
            chapter = chapter,
            lines = [],
            images = byte_images,
            titles = KeyResult(
                chapter=f'memes: [{", ".join(subreddits)}]',
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                chapter = None,
                story = None,
                domain = None,
            ),
        );
        
    def getConfiguration(self, url: str):
        return None;