import json
import requests;
from models.scraper_result import ScraperResult
from models.story_type import StoryType
from models.driver import Driver
from selectolax.parser import HTMLParser, Node;
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
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
        manga_uuid = next(x for x in relationships if x['type'] == 'manga')['id'];
        group_uuid = next(x for x in relationships if x['type'] == 'scanlation_group')['id'];


        story_url = f"https://api.mangadex.org/manga/{manga_uuid}/aggregate?translatedLanguage[]=en&groups[]={group_uuid}";
        story_content = self._try_get_json(story_url, self._session);
        volumes = self.walk(story_content, 'volumes');
        chapters = [];
        for volume in volumes.values():
            for chap in volume['chapters'].values():
                chapters.append(chap);
        chapters.sort(key=lambda x: self.zpad(x['chapter'], 5), reverse=False)
        chapter_index = next(index for index, chap in enumerate(chapters) if chap['id'] == chapter_uuid);

        next_chapter = chapters[chapter_index + 1] if len(chapters) > chapter_index + 1 else None;
        prev_chapter = chapters[chapter_index - 1] if chapter_index > 0 else None;

        prefix = "https://mangadex.org/chapter/";
        self._result = ScraperResult(
            story_type = StoryType.MANGA,
            urls = self.Object(
                prev = prefix + prev_chapter['id'] if prev_chapter else None,
                current = url,
                next = prefix + next_chapter['id'] if next_chapter else None,
            ),
            chapter = chapter,
            lines = [],
            images = byte_images,
            title = ' - '.join([attributes.get('chapter'), attributes.get('title')]) if attributes.get('title') else attributes.get('chapter'),
            keys = self.Object(
                chapter = chapter_uuid,
                story = manga_uuid
            ),
        );
    
    def zpad(self, val, n):
        bits = val.split('.')
        if len(bits) < 2:
            return bits[0].zfill(n);
        return "%s.%s" % (bits[0].zfill(n), bits[1])
        
    def setupSession(self, url: str, session_dict: dict[str, requests.Session]):
        sections = url.split('/');
        base_url = "/".join(sections[:3]);
        domainSections = sections[2].split('.');
        if domainSections[0] == 'www':
            domainSections = domainSections[1:];
        site_key = '_'.join(domainSections);
        if not session_dict.get(site_key):
            session_dict[site_key] = requests.Session();
            session_dict[site_key].post(base_url, headers=self.headers)
        return site_key;

    def getVolumeChapterIndeces(self, volumes, chapter_uuid):
        for v_index, (v_key, volume) in enumerate(volumes.items()):
            chapters = self.walk(volume, 'chapters')
            for c_index, (c_key, chapter) in enumerate(chapters.items()):
                if chapter['id'] == chapter_uuid:
                    return v_index, c_index;
    
    def walk(self, object:dict, path: str):
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
        
    def getConfiguration(self, url):
        return None;