import requests
import re
from selectolax.parser import HTMLParser, Node
from models.scraper_result import ScraperResult;
from models.story_type import StoryType
from models.driver import Driver
from scrape.basic_scraper import BasicConfiguration;
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        # super().useHtml(url);
        super().useDriver(url, driver);
        # super().useReDriver(url, driver);
        # super().useSession(url, session_dict);

    def _scrape(self, body: Node):
        urls_finds = re.findall(r'("https?://[^\s]+")', body.html);
        urls = [url[1:-1] for url in urls_finds if url.endswith('.jpg"') and url.find('hentai20.io') == -1];
        sections = self._url.split('/');
        img_element = lambda src: f'<img src="{src}"></img>'; 
        img_elements = map(lambda x: img_element(x), urls);
        chapter = HTMLParser(f'<div>{"".join(img_elements)}</div>').body
        byte_images = self._get_images_from_tags(img_tags=chapter.css('img'));
        buttons = self._configuration.get_buttons(body);
        story_type = self._configuration.get_story_type(body, sections);
        return ScraperResult(
            story_type = story_type,
            urls = self._configuration.get_urls(buttons),
            chapter = chapter,
            lines = None,
            images = byte_images,
            title = self._configuration.get_title(body).text(),
            keys = self._configuration.get_keys(body, sections),
        )

    def getConfiguration(self, url):
        return BasicConfiguration(
            get_story_type = lambda node, sections: StoryType.MANGA,
            src = 'src',
            get_title = lambda node: node.css_first('.entry-title'),
            get_chapter = lambda node, sections: node.css_first('.reading-content'),
            get_buttons = lambda node: self.Object(
                prev = node.css_first('.nextprev .ch-prev-btn'),
                next = node.css_first('.nextprev .ch-next-btn'),
            ),
            get_urls = lambda buttons: self.Object(
                prev = self.tryGetHref(buttons.prev),
                current = url,
                next = self.tryGetHref(buttons.next),
            ),
            get_keys = lambda node, sections: self.Object(
                story = '-'.join(sections[3].split('-')[:-2]),
                chapter = '-'.join(sections[3].split('-')[-2:]),
            ),
        );