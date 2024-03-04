import requests
from helpers.driver import Driver
from scrape.mangas.asuratoon_com import SiteScraper as Asuratoon;

class SiteScraper(Asuratoon):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
        super().__init__(url.replace('asurascans.com', 'asuratoon.com', 1), driver, session_dict);

# class SiteScraper(ConfigureSiteScraper):
#     def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
#         # super().useHtml(url);
#         super().useDriver(url, driver);
#         # super().useReDriver(url, driver);
#         # super().useSession(url, session_dict);
        
#     def getConfiguration(self, url: str):
#         return BasicConfiguration(
#             get_story_type = lambda node, sections: StoryType.MANGA,
#             src = 'src',
#             get_chapter = lambda node, sections: node.css_first('#readerarea'),
#             get_titles = lambda node, sections: self.get_titles(node, sections),
#             get_urls = lambda node, sections: self.get_urls(node, sections, url),
#             get_keys = lambda node, sections: KeyResult(
#                 story = "-".join(sections[3].split('-')[:-2]),
#                 chapter = "-".join(sections[3].split('-')[-2:]),
#                 domain = None,
#             ),
#         );

#     def get_titles(self, node: Node, sections: list[str]):
#         chapter = node.css_first('h1.entry-title')
#         return KeyResult(
#             chapter = chapter.text(),
#             domain = None,
#             story = None,
#         );

#     def get_urls(self, node: Node, sections: list[str], url: str):
#         prev = node.css_first('.nextprev a.ch-prev-btn');
#         next = node.css_first('.nextprev a.ch-next-btn');
#         return UrlResult(
#                 prev = self.tryGetHref(prev),
#                 current = url,
#                 next = self.tryGetHref(next),
#         );