import json;
import requests;
from models.scraper_result import ScraperResult
from models.story_type import StoryType
from models.driver import Driver
from selectolax.parser import HTMLParser, Node
from scrape.basic_scraper import BasicConfiguration
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        # super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        super().useSession(url, session_dict);

    # def _scrape(self, body: Node):
    #     prefix = 'https://api.omegascans.org/';
    #     sections = self._url.split('/');
    #     script_element = body.css_first('#__NEXT_DATA__');
    #     json_script_element = json.loads(script_element.text());
    #     chapter_id = self.walk(json_script_element, 'props.pageProps.data.id');
    #     content = self._try_get_content(f'{prefix}series/chapter/{chapter_id}', self._driver, self._session);
    #     json_content = json.loads(content);
    #     images = self.walk(json_content, 'content.images');
    #     img_element = lambda src: f'<img src="{src if src.startswith("http") else prefix + src}"></img>'; 
    #     img_elements = map(lambda x: img_element(x), images);
    #     chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
    #     byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
    #     buttons = self._configuration.get_buttons(body);
    #     story_type = self._configuration.get_story_type(body, sections);
    #     return ScraperResult(
    #         story_type = story_type,
    #         urls = self._configuration.get_urls(buttons),
    #         chapter = chapter,
    #         lines = None,
    #         images = byte_images,
    #         title = self._configuration.get_title(body).text(),
    #         keys = self._configuration.get_keys(body, sections),
    #     )
    
    # def walk(self, object:dict, path):
    #     routes = path.split('.');
    #     result = None;
    #     for route in routes:
    #         if route not in object:
    #             print(f'Images not found using path: {path}');
    #             return None;
    #         result = object[route];
    #     return result;
        
    # def getConfiguration(self, url):
    #     prefix = 'https://omegascans.org';
    #     return BasicConfiguration(
    #         get_story_type = lambda node, sections: StoryType.MANGA,
    #         src = 'src',
    #         get_title = lambda node: node.css_first('.chapter-heading h5'),
    #         get_chapter = lambda node, sections: node.css_first('.main-content div:nth-child(3)'),
    #         get_buttons = lambda node: self.Object(
    #             prev = node.css_first('.sub-nav .prev-chap a'),
    #             next = node.css_first('.sub-nav .next-chap a'),
    #         ),
    #         get_urls = lambda buttons: self.Object(
    #             prev = self.tryGetHref(buttons.prev, prefix, lambda element: not element.css_first('svg.fa-house-user')),
    #             current = url,
    #             next = self.tryGetHref(buttons.next, prefix, lambda element: not element.css_first('svg.fa-house-user')),
    #         ),
    #         get_keys = lambda node, sections: self.Object(
    #             story = sections[4],
    #             chapter = sections[5],
    #         ),
    #     );
        
    def getConfiguration(self, url):
        prefix = 'https://omegascans.org';
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.MANGA,
            src = lambda node: node.attributes.get('data-src') or node.attributes.get('src'),
            get_title = lambda node: node.css_first('.container > div.flex h1'),
            get_chapter = lambda node, sections: node.css_first('.container > p.flex'),
            get_buttons = lambda node: self.Object(
                prev = node.css('.container > div.flex > a')[1],
                next = node.css('.container > div.flex > a')[-1],
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev, prefix, lambda element: len(element.attributes.get('href').split('/')) == 4),
                current = url,
                next = self.tryGetHref(buttons.next, prefix, lambda element: len(element.attributes.get('href').split('/')) == 4),
            ),
            get_keys = lambda node, sections: self.Object(
                story = sections[4],
                chapter = sections[5],
            ),
        );
