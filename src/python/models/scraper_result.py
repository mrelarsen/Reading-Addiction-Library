from threading import Thread
from typing import Any
from models.story_type import StoryType
from selectolax.parser import Node

class ScraperResult():
    def __init__(self, urls, story_type: StoryType, title, keys, images: list[str]=None, chapter: Node=None, lines: list[Node]=None, urllist: list = None, loading = False, driver_required = False, driver_requires_reset = False):
        self.urls: Any = urls;
        self.urllist = urllist;
        self.story_type = story_type;
        self.chapter = chapter;
        self.lines = lines; # novels
        self.images = images; # manga
        self.title: Any = title;
        self.keys: Any = keys;
        self.loading = driver_requires_reset or driver_required or loading;
        self.driver_required = driver_requires_reset or driver_required;
        self.driver_requires_reset = driver_requires_reset;
        self.domain = None;
        self.counter = 1;
    
    def is_loading(self):
        return self.loading or self.driver_required or self.driver_requires_reset;

    def get_with_domain(self, domain=None):
        self.domain = domain;
        return self;

    def asDictionary(self):
        return {
            'urls': self.urls,
            'urllist':self.urllist,
            'story_type':self.story_type,
            'chapter':self.chapter,
            'lines':self.lines,
            'images':self.images,
            'title':self.title,
            'keys': {'story':self.keys.story, 'chapter':self.keys.chapter},
            'loading':self.loading,
            'driver_required':self.driver_required,
            'driver_requires_reset':self.driver_requires_reset}