import requests
from helpers.driver import Driver
from helpers.story_type import StoryType
from scrape.mangas.asuracomic_net import SiteScraper as Asuratoon;

def get_story_type(sections) -> StoryType:
    return StoryType.MANGA;
get_story_type=lambda node, sections: get_story_type(sections),

class SiteScraper(Asuratoon):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        super().__init__(url.replace('asuracomics.com', 'asuracomic.net', 1), driver, session_dict, headers);

# class SiteScraper(ConfigureSiteScraper):
#     def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session]):
#         # super().useHtml(url, headers);
#         super().useDriver(url, driver);
#         # super().useReDriver(url, driver, headers);;
#         # super().useSession(url, session_dict, headers);
        
#     def getConfiguration(self, url: str):
#         return BasicConfiguration(
#             get_story_type = lambda node, sections: get_story_type(sections),
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
#             prev = self.tryGetHref(prev),
#             current = url,
#             next = self.tryGetHref(next),
#         );