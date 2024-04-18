import json;
import requests;
from helpers.scraper_result import ScraperResult
from helpers.story_type import StoryType
from helpers.driver import Driver
from selectolax.parser import HTMLParser, Node
from scrape.configure_site_scraper import ConfigureSiteScraper;
from helpers.scraper_result import KeyResult, UrlResult;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);

    def _scrape(self, body: Node):
        prefix = 'https://mangapark.net';
        sections = self._url.split('/');
        script_element = body.css_first('#__NEXT_DATA__');
        json_script_element = json.loads(script_element.text());
        chapter_data = self.walk(json_script_element, 'props.pageProps.dehydratedState.queries.0.state.data.data');
        img_element = lambda src: f'<img src="{src}"></img>'; 
        concat=[]
        for i in range(len(self.walk(chapter_data, 'imageSet.httpLis'))):
            concat.append(f"{self.walk(chapter_data, 'imageSet.httpLis')[i]}?{self.walk(chapter_data, 'imageSet.wordLis')[i]}")
        img_elements = map(lambda x: img_element(x), concat);
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
        story_id = self.walk(chapter_data, 'comicNode.data.id');
        sourceId = chapter_data['sourceId'];
        lang = chapter_data['lang'];
        request = self.makeRequest(story_id, chapter_data['serial'], lang);
        content = json.loads(self._session.post(f'{prefix}/apo/', json=request, headers=self._headers).content);
        next_chapters = self.walk(content, 'data.get_content_chapterSiblings.nextNodes');
        next_chapter_same_source = lambda: next_chapters and next(x for x in next_chapters if self.walk(x, 'data.sourceId') == sourceId and self.walk(x, 'data.lang') == lang);
        next_chapter_next_source = lambda: next_chapters and next(x for x in next_chapters if self.walk(x, 'data.lang') == lang);
        next_chapter = next_chapter_same_source() or next_chapter_next_source();
        prev_chapters = self.walk(content, 'data.get_content_chapterSiblings.prevNodes');
        prev_chapter_same_source = lambda: prev_chapters and next(x for x in prev_chapters if self.walk(x, 'data.sourceId') == sourceId and self.walk(x, 'data.lang') == lang);
        prev_chapter_next_source = lambda: prev_chapters and next(x for x in prev_chapters if self.walk(x, 'data.lang') == lang);
        prev_chapter = prev_chapter_same_source() or prev_chapter_next_source();
        return ScraperResult(
            story_type = get_story_type(sections),
            urls = UrlResult(
                prev = prefix + self.walk(prev_chapter, 'data.urlPath') if prev_chapter else None,
                current = prefix + chapter_data['urlPath'],
                next = prefix + self.walk(next_chapter, 'data.urlPath') if next_chapter else None,
            ),
            chapter = chapter,
            lines = None,
            images = byte_images,
            titles = KeyResult(
                chapter = chapter_data['dname'],
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                chapter = str(chapter_data['id']),
                story = str(story_id),
                domain = None,
            ),
        );
    
    def makeRequest(self, story_id: str, serial: str, lang: str):
        return {
            "operationName": "get_content_chapterSiblings",
            "query": "\n  query get_content_chapterSiblings($comicId:Int!, $serial:Float!, $lang:String) {\n    get_content_chapterSiblings(comicId:$comicId, serial:$serial, lang:$lang) {\n      \n      serialList\n\n      prevSerial\n      currSerial\n      nextSerial\n\n      prevNodes {\n        \n  id\n  data {\n    \n\n  id\n  sourceId\n\n  dbStatus\n  isNormal\n  isHidden\n  isDeleted\n  isFinal\n  \n  dateCreate\n  datePublic\n  dateModify\n  lang\n  volume\n  serial\n  dname\n  title\n  urlPath\n\n  srcTitle srcColor\n\n  count_images\n\n  stat_count_post_child\n  stat_count_post_reply\n  stat_count_views_login\n  stat_count_views_guest\n  \n  userId\n  userNode {\n    \n  id \n  data {\n    \nid\nname\nuniq\navatarUrl \nurlPath\n\nverified\ndeleted\nbanned\n\ndateCreate\ndateOnline\n\nstat_count_chapters_normal\nstat_count_chapters_others\n\nis_adm is_mod is_vip is_upr\n\n  }\n\n  }\n\n  disqusId\n\n\n  }\n\n        sser_read\n      }\n      sameNodes {\n        \n  id\n  data {\n    \n\n  id\n  sourceId\n\n  dbStatus\n  isNormal\n  isHidden\n  isDeleted\n  isFinal\n  \n  dateCreate\n  datePublic\n  dateModify\n  lang\n  volume\n  serial\n  dname\n  title\n  urlPath\n\n  srcTitle srcColor\n\n  count_images\n\n  stat_count_post_child\n  stat_count_post_reply\n  stat_count_views_login\n  stat_count_views_guest\n  \n  userId\n  userNode {\n    \n  id \n  data {\n    \nid\nname\nuniq\navatarUrl \nurlPath\n\nverified\ndeleted\nbanned\n\ndateCreate\ndateOnline\n\nstat_count_chapters_normal\nstat_count_chapters_others\n\nis_adm is_mod is_vip is_upr\n\n  }\n\n  }\n\n  disqusId\n\n\n  }\n\n        sser_read\n      }\n      nextNodes {\n        \n  id\n  data {\n    \n\n  id\n  sourceId\n\n  dbStatus\n  isNormal\n  isHidden\n  isDeleted\n  isFinal\n  \n  dateCreate\n  datePublic\n  dateModify\n  lang\n  volume\n  serial\n  dname\n  title\n  urlPath\n\n  srcTitle srcColor\n\n  count_images\n\n  stat_count_post_child\n  stat_count_post_reply\n  stat_count_views_login\n  stat_count_views_guest\n  \n  userId\n  userNode {\n    \n  id \n  data {\n    \nid\nname\nuniq\navatarUrl \nurlPath\n\nverified\ndeleted\nbanned\n\ndateCreate\ndateOnline\n\nstat_count_chapters_normal\nstat_count_chapters_others\n\nis_adm is_mod is_vip is_upr\n\n  }\n\n  }\n\n  disqusId\n\n\n  }\n\n        sser_read\n      }\n    }\n  }\n  ",
            "variables": {
                "comicId": story_id,
                "lang": lang,
                "serial": serial
            }
        };
    
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