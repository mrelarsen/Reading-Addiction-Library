import requests
from selectolax.parser import HTMLParser
from helpers.scraper_result import ScraperResult;
from helpers.story_type import StoryType
from helpers.driver import Driver
from scrape.configure_site_scraper import ConfigureSiteScraper;
from helpers.scraper_result import KeyResult, UrlResult;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        # super().useSession(url, session_dict);
        self._url = url;
        self._headers = self.headers;
        sections = url.split('/');
        site_key = self.setupSession(url, session_dict);
        sections = url.split('/');
        manga_uuid = sections[4];
        chapter_uuid = sections[6];
        chapter_url = f'https://backend.hentaidexy.net/api/v1/chapters/{chapter_uuid}'
        chapters_url = f'https://backend.hentaidexy.net/api/v1/mangas/{manga_uuid}/chapters?fields=_id,serialNumber&sort=serialNumber&limit=999999'
        self._session = session_dict.get(site_key);

        chapter_content = self._try_get_json(chapter_url, self._session, self.headers);
        img_urls = self.walk(chapter_content, 'chapter.images');
        img_element = lambda src_file: f'<img src="https://s1.cdnimg.me:9000/hentaidexy/{src_file}"></img>'; 
        img_elements = map(lambda src: img_element(src.split('/')[-1]), img_urls);
        data_chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=data_chapter.css('img'));

        chapters_content = self._try_get_json(chapters_url, self._session, self.headers);
        chapters = self.walk(chapters_content, 'chapters');
        chapter = next((x for x in chapters if x['_id'] == chapter_uuid), None);
        chapter_number: int = chapter['serialNumber'] if chapter else -1000;
        prev_chapter = next((x for x in chapters if x['serialNumber'] == chapter_number - 1), None);
        next_chapter = next((x for x in chapters if x['serialNumber'] == chapter_number + 1), None);

        self._result = ScraperResult(
            story_type = StoryType.MANGA,
            urls = UrlResult(
                prev = "/".join(sections[:-1] + [prev_chapter['_id']]) if prev_chapter else None,
                current = url,
                next = "/".join(sections[:-1] + [next_chapter['_id']]) if next_chapter else None,
            ),
            chapter = data_chapter,
            lines = [],
            images = byte_images,
            titles = KeyResult(
                chapter=f'Chapter {chapter_number}',
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                chapter = chapter_uuid,
                story = manga_uuid,
                domain = None,
            )
        );
    
    def walk(self, object: dict, path: str):
        routes = path.split('.');
        result = object;
        for route in routes:
            if route.isdigit():
                index = int(route);
                if len(result) <= index:
                    print(f'Cannot read index: {index}/{len(result)}, on {result}');
                    return None;
                result = result[index];
                continue;
            if route not in result:
                print(f'Cannot walk path: {path}, beyond {route}, on {result}');
                return None;
            result = result[route];
        return result;
        
    def getConfiguration(self, url: str):
        return None;