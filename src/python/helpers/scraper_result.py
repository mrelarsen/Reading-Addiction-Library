from typing import Optional
from helpers.joke import Joke
from helpers.story_type import StoryType
from selectolax.parser import HTMLParser, Node
from helpers.meme import Meme

class KeyResult():
    def __init__(self, story: str|None, domain: str|None, chapter: str|None) -> None:
        self.story = story;
        self.domain = domain;
        self.chapter = chapter;

    def asDictionary(self):
        return {
            'story': self.story,
            'domain':self.domain,
            'chapter':self.chapter}
    
class UrlResult():
    def __init__(self, prev: str|None, current: str, next: str|None) -> None:
        self.prev = prev;
        self.current = current;
        self.next = next;

    def asDictionary(self):
        return {
            'prev': self.prev,
            'current':self.current,
            'next':self.next}

class ScraperResult():
    def __init__(self, urls: UrlResult, story_type: StoryType, titles: KeyResult, keys: KeyResult, images: list[str]|None=None, chapter: Node=None, lines: list[Node]|None=None, urllist: list|None = None, loading = False, driver_required = False, driver_requires_reset = False):
        self.urls = urls;
        self.titles = titles;
        self.keys = keys;
        self.urllist = urllist;
        self.story_type = story_type;
        self.chapter = chapter;
        self.lines = lines; # novels
        self.images = images; # manga
        self.loading = driver_requires_reset or driver_required or loading;
        self.driver_required = driver_requires_reset or driver_required;
        self.driver_requires_reset = driver_requires_reset;
        self.counter = 1;
    
    def is_loading(self):
        return self.loading or self.driver_required or self.driver_requires_reset;

    def get_with_domain(self, domain=None):
        self.keys.domain = domain;
        return self;

    def asDictionary(self):
        return {
            'urls': self.urls.asDictionary(),
            'urllist':self.urllist,
            'story_type':self.story_type,
            'chapter':self.chapter,
            'lines':self.lines,
            'images':self.images,
            'titles':self.titles.asDictionary(),
            'keys':self.keys.asDictionary(),
            'loading':self.loading,
            'driver_required':self.driver_required,
            'driver_requires_reset':self.driver_requires_reset}

    def get_ensuing_url(self, dir: int):
        if dir < 0:
            return self.urls.prev;
        if dir == 0:
            return self.urls.current;
        if dir > 0:
            return self.urls.next;
    
    def updateLoading(self, type: StoryType):
        if self.is_loading():
            loading = ScraperResult._get_waiting(self.urls.current, self.urls.current, type);
            self.chapter = loading.chapter;
            self.lines = loading.lines;
            self.images = loading.images;
            self.counter += 1;

    @staticmethod
    def _get_default_tts(texts: list, title: str, url:str, next_url: Optional[str] = None, loading = False, driver_required = False, driver_requires_reset = False):
        spans =  map(lambda x: f"<div>{x}</div>", texts);
        chapter = HTMLParser(f"<div>{''.join(spans)}</div>").body.child;
        return ScraperResult(
            story_type=StoryType.NOVEL,
            urls = UrlResult(prev=None, current = url, next=next_url),
            chapter = chapter,
            lines = ScraperResult.get_lines(chapter),
            titles = KeyResult(
                chapter=title,
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                story=None,
                chapter=None,
                domain = None,
            ),
            loading = loading,
            driver_required = driver_required,
            driver_requires_reset = driver_requires_reset,
        )
    
    @staticmethod
    def _get_default_image(images: list, title: str, url:str, next_url: Optional[str] = None, loading = False, driver_required = False, driver_requires_reset = False):
        chapter = HTMLParser(f"<div></div>").body.child;
        return ScraperResult(
            story_type=StoryType.MANGA,
            urls = UrlResult(prev=None, current = url, next=next_url),
            chapter = chapter,
            lines = ScraperResult.get_lines(chapter),
            images = images,
            titles = KeyResult(
                chapter=title,
                domain = None,
                story = None,
            ),
            keys = KeyResult(
                story=None,
                chapter=None,
                domain = None,
            ),
            loading = loading,
            driver_required = driver_required,
            driver_requires_reset = driver_requires_reset,
        )

    @staticmethod
    def get_lines(node: Node, depth = 0):
        text = node.text(strip=True)
        if node.tag != '-text':
            childLines = []
            child = node.child;
            while child:
                childLines.extend(ScraperResult.get_lines(child, depth + 1));
                child = child.next;
            return childLines;
        elif text != "" and node.parent != None:
            return [node];
        return []

    @staticmethod
    def _get_error(error, url: str, loading = False):
        print('An error occurred while parsing the url!', 'Url:', url, 'Error:', error);
        return ScraperResult._get_default_tts(
            texts = ['An error occurred while parsing the url!', 'Url:', url, 'Error:', str(error)],
            title = 'An error occurred while parsing the url!',
            url = url,
            loading=loading);

    @staticmethod
    def _get_cannot_parse(url: str, driver_requires_reset = False):
        return ScraperResult._get_default_tts(
            texts = ['Failed to parse content of the url!', 'Url:', url],
            title = 'Cannot parse the url!',
            url = url,
            next_url=url if driver_requires_reset else None,
            driver_requires_reset=driver_requires_reset);

    @staticmethod
    def get_entertaiment_by_story_type(type: StoryType = StoryType.NOVEL):
        if (type == StoryType.MANGA):
            meme = Meme();
            return meme.texts, meme.title, meme.images;
        if (type == StoryType.NOVEL):
            joke = Joke();
            return ([joke.type] + joke.texts), None, None;
        return ['Error finding entertainment'], 'Entertainment error', None;
    
    @staticmethod
    def _get_waiting_empty(url: str, next_url: str):
        return ScraperResult._get_default_tts(
            texts = ['Loading'],
            title = 'Loading site',
            url = url,
            next_url = next_url,
            loading = True);
    
    @staticmethod
    def _get_waiting(url: str, next_url: str, type: StoryType):
        texts, title, images = ScraperResult.get_entertaiment_by_story_type(type);
        if images:
            return ScraperResult._get_default_image(
                images = images,
                title = title or 'Loading site',
                url = url,
                next_url = next_url,
                loading = True);
        return ScraperResult._get_default_tts(
            texts = ['Loading'] + texts,
            title = title or 'Loading site',
            url = url,
            next_url = next_url,
            loading = True);
    
    @staticmethod
    def _get_driver_required(url: str, type: StoryType):
        texts, title, images = ScraperResult.get_entertaiment_by_story_type(type);
        if images:
            return ScraperResult._get_default_image(
                images = images,
                title = title or 'Loading site',
                url = url,
                next_url = url,
                driver_required = True);
        return ScraperResult._get_default_tts(
            texts = ['Loading'] + texts,
            title = title or 'Starting driver for website',
            url = url,
            next_url = url,
            driver_required = True);
    
    @staticmethod
    def _get_driver_requires_reset(url: str, type: StoryType):
        texts, title, images = ScraperResult.get_entertaiment_by_story_type(type);
        if images:
            return ScraperResult._get_default_image(
                images = images,
                title = title or 'Resetting driver for website',
                url = url,
                next_url = url,
                driver_required = True,
                driver_requires_reset = True);
        return ScraperResult._get_default_tts(
            texts = ['Resetting'] + texts,
            title = title or 'Starting driver for website',
            url = url,
            next_url = url,
            driver_required = True,
            driver_requires_reset = True);
    
