import requests
import json;
from helpers.scraper_result import ScraperResult
from helpers.story_type import StoryType
from helpers.driver import Driver
from selectolax.parser import HTMLParser;
from scrape.configure_site_scraper import ConfigureSiteScraper;
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

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
        chapter_uuid = sections[4];
        chapter_url = f"https://api.mangadex.org/at-home/server/{chapter_uuid}?forcePort443=false";
        self._session = session_dict.get(site_key);
        chapter_content = self._try_get_json(chapter_url, self._session, self.headers);
        img_urls = self.walk(chapter_content, 'chapter.data');
        hash = self.walk(chapter_content, 'chapter.hash');
        
        img_element = lambda src: f'<img src="https://uploads.mangadex.org/data/{hash}/{src}"></img>'; 
        img_elements = map(lambda x: img_element(x), img_urls);
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));

        chapter_info_url = f"https://api.mangadex.org/chapter/{chapter_uuid}?includes[]=scanlation_group&includes[]=manga&includes[]=user";
        chapter_info_content = self._try_get_json(chapter_info_url, self._session);
        
        relationships = self.walk(chapter_info_content, 'data.relationships');
        attributes = self.walk(chapter_info_content, 'data.attributes');
        # print(json.dumps(relationships));
        manga_uuid = next((x for x in relationships if x['type'] == 'manga'), { 'id': None })['id'];
        group_uuid = next((x for x in relationships if x['type'] == 'scanlation_group'), { 'id': None })['id'];
        user_uuid = next((x for x in relationships if x['type'] == 'user'), { 'id': None })['id'];
        if not manga_uuid:
            self._result = ScraperResult._get_default_tts(
                texts = ['Manga could not be found!', 'Url:', url],
                title = 'Manga could not be found while parsing the url!',
                url = url,
                loading=False);
            return;
        creator_uuid = group_uuid or user_uuid;
        if not creator_uuid:
            self._result = ScraperResult._get_default_tts(
                texts = ['Manga creator could not be found!', 'Url:', url],
                title = 'Manga creator could not be found while parsing the url!',
                url = url,
                loading=False);
            return;

        story_url = f"https://api.mangadex.org/manga/{manga_uuid}/aggregate?translatedLanguage[]={attributes['translatedLanguage'] or 'en'}&groups[]={group_uuid}";
        if not group_uuid:
            story_url = f"https://api.mangadex.org/manga/{manga_uuid}/aggregate?translatedLanguage[]={attributes['translatedLanguage'] or 'en'}";
        story_content = self._try_get_json(story_url, self._session);
        chapters = [];
        chapter_index = 0;
        result = self.walk(story_content, 'result');
        if result and result == 'error':
            print("An error occured fetching next and previous chapter", json.dumps(story_content), story_url);
        else:
            volumes = self.walk(story_content, 'volumes');
            for volume in volumes.values():
                for chap in volume['chapters'].values():
                    chapters.append(chap);
            chapters.sort(key=lambda x: self.zpad(x['chapter'], 5), reverse=False)
            chapter_index = next(index for index, chap in enumerate(chapters) if chap['id'] == chapter_uuid);

        next_chapter = chapters[chapter_index + 1] if len(chapters) > chapter_index + 1 else None;
        prev_chapter = chapters[chapter_index - 1] if chapter_index > 0 else None;

        prefix = "https://mangadex.org/chapter/";
        self._result = ScraperResult(
            story_type = get_story_type(sections),
            urls = UrlResult(
                prev = prefix + prev_chapter['id'] if prev_chapter else None,
                current = url,
                next = prefix + next_chapter['id'] if next_chapter else None,
            ),
            chapter = chapter,
            lines = [],
            images = byte_images,
            titles = KeyResult(
                chapter=' - '.join([attributes.get('chapter'), attributes.get('title')]) if attributes.get('title') else attributes.get('chapter'),
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                chapter = chapter_uuid,
                story = manga_uuid,
                domain = None,
            ),
        );
    
    def zpad(self, val: str, n: int):
        bits = val.split('.')
        if len(bits) < 2:
            return bits[0].zfill(n);
        return "%s.%s" % (bits[0].zfill(n), bits[1])

    def getVolumeChapterIndeces(self, volumes: dict[str, dict[str, dict]], chapter_uuid: str):
        for v_index, (v_key, volume) in enumerate(volumes.items()):
            chapters = self.walk(volume, 'chapters')
            for c_index, (c_key, chapter) in enumerate(chapters.items()):
                if chapter['id'] == chapter_uuid:
                    return v_index, c_index;
    
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