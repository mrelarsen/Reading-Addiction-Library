import html as htmlParser;
import importlib
import json;
import os
import threading
import pyperclip as pc;
import re;
import sciter;
import webbrowser
from database.history import History
from helpers.driver import Driver
from helpers.reading_status import ReadingStatus
from helpers.story_type import StoryType;
from selectolax.parser import HTMLParser, Node
from helpers.text_helper import TextHelper;
from scrape.basic_scraper import BasicScraper, ScraperResult, KeyResult, UrlResult;
from helpers.scrape_service import ScrapeService
from helpers.tts_reader import TTSReader
from time import sleep
from typing import Any, Callable, Optional

cssutils_spec = importlib.util.find_spec("cssutils")
if cssutils_spec:
    from cssutils import CSSParser
    
class WordMatch():
    def __init__(self, match: re.Match):
        self.value = match.group(0)
        self.start = match.start(0)
        self.end = match.end(0)

class ReaderEventHandler():
    def __init__(self, el: sciter.dom.Element, settings: dict, history: History, call_javascript: Callable[[str, list[Any]], None], driver: Driver):
        self.element=el;
        self.history = history;
        self.driver: Driver = driver;
        self.selector = '#rdr_content';
        self.word_callback = self.on_word;
        self.scrape_service = ScrapeService(self.history, self.driver, settings.get('story_headers', {}));
        self.tts_reader = TTSReader(settings=settings, word_callback=self.word_callback);
        self.auto_scroll = settings.get('auto_scroll') if settings.get('auto_scroll') == False else True;
        self.line: Optional[str] = None;
        self.line_prefix = '<div style="padding-left:3px;padding-right:3px">';
        self.chapter: dict[str, Node] = {};
        self.line_number = 0;
        self.auto_continuation = settings.get('auto_continuation') if settings.get('auto_continuation') == False else True;
        self.call_javascript = call_javascript;
        self.text_size = settings.get('text_size') or 1;
        self.use_tts = settings.get('use_tts') if settings.get('use_tts') == False else True;
        self.number_of_words = 1;
        self.number_of_characters = 1;
        self.word_matches: list[list[WordMatch]] = [];
        self.reading_timer: threading.Thread|None = None;
        self.html_list = [];
        self.html_index = 0;
        self.parser = None;
        if cssutils_spec:
            self.parser = CSSParser();
        pass

    def set_settings(self, settings: dict):
        self.tts_reader.set_settings(settings);
        self.scrape_service.async_scraper.queueWorker.set_story_headers(settings.get('story_headers', {}));

    @sciter.script('get_settings')
    def get_settings(self) -> dict:
        return {
            "auto_continuation": self.auto_continuation,
            "auto_scroll": self.auto_scroll,
            "use_tts": self.use_tts,
            "text_size": self.text_size,
            "rate": self.tts_reader.get_rate(),
            "volume": self.tts_reader.get_volume(),
            "voice": self.tts_reader.get_voice(),
            # Not saved values:
            "driver": self.driver.is_running(),
            "voices": self.tts_reader.get_voices(),
        };

    @sciter.script('reset_reader')
    def reset_reader(self):
        self.tts_reader.reset_pyttsx3();

    @sciter.script('download_list')
    def download_list(self, text: str, chapter_depth: int = 1):
        self.html_list = [];
        urllist = [x for x in re.split(r'[\s,]', text) if x and re.match(r'^!?(http|file)', x)];
        print(urllist)
        self.download(chapter_depth, urllist);
        pass

    def download(self, chapter_depth = 1, urllist: list[str] = []):
        for i in range(len(urllist)):
            is_continuous, url = self.get_continuous_url(urllist[i]);
            result = self.download_chapter(url);
            counter = 1;
            while is_continuous and result and result.urls.next and counter < chapter_depth:
                result = self.download_chapter(result.urls.next);
                counter += 1;
        print('Done downloading!');

    def download_chapter(self, url: str):
        _, result = self.scrape_service.read_info(url=url, buffer=False, loading=False);
        while result.is_loading():
            sleep(0.5);
            _, result = self.scrape_service.read_info(url=url, buffer=False, loading=False);
        sections = [x for x in re.split(r'[/.-]', result.keys.story) if x];
        abbreviation = "".join(map(lambda x: x[0], sections)) if len(sections) > 1 else result.keys.story;
        chapter_id = self.scrape_service.try_to_save(ReadingStatus.DOWNLOADED);
        title = "-".join(x for x in re.split(r'[\s/.,:-?]', result.titles.chapter) if x);
        text = result.chapter.text(deep=True, strip=True);
        self.tts_reader.download(text=text, save_path='downloads/wavs/', file_name=f'{abbreviation}-{chapter_id}-{title}');
        return result;

    def get_continuous_url(self, url):
        return (False, url) if url[0] != '!' else (True, url[1:]);

    @sciter.script('read_list')
    def read_list(self, text: str, next = False):
        urllist = [x for x in re.split(r'[\s,]', text) if x and re.match(r'^!?(http|file|meme)', x)];
        self.html_list = [];
        print(urllist)
        if not next:
            self.read(urllist=urllist);
        else:
            if self.scrape_service.result and (self.scrape_service.result.urls.current not in urllist or f'!{self.scrape_service.result.urls.current}' not in urllist):
                urllist = [self.scrape_service.result.urls.current] + urllist;
            self.scrape_service.urllist = urllist;
        pass

    @sciter.script('read')
    def read(self, dir = 0, force = False, urllist: Optional[list[str]] = None):
        story_type, result = self.scrape_service.read_info(dir=dir, urllist=urllist);
        if story_type == StoryType.NOVEL:
            self.read_tts(result=result, force=force);
        elif story_type == StoryType.MANGA:
            self.read_manga(result=result);
        else:
            print('Url not found or wrong format!');

    def read_tts(self, result: ScraperResult, force: bool):
        TextHelper.clean_html(result, self.parser);
        lines = self.set_lines(result);
        self.setup_chapter(result);
        self.element.find_first('#rdr_lbl_title').text = result.titles.chapter;
        if result.keys.domain:
            story, key = self.scrape_service.get_story();
            if story or result.titles.story:
                self.element.find_first('#rdr_lbl_story_title').text = (story and story.get('name')) or result.titles.story or '';
            self.scrape_service.try_to_save(ReadingStatus.READING);
        self.set_urls();
        self.lineNumber = 0;
        self.scroll();
        if self.use_tts:
            self.tts_reader.read(lines=lines, force=force, update_callback=self.update_text_view, completed_callback=self.on_read_completion)
        else:
            self.tts_reader.quit(callback=lambda: self.start_reader());
        
    def set_lines(self, result: ScraperResult):
        lines = [];
        words: list[list[WordMatch]] = [];
        for idx, line in enumerate(result.lines):
            line_with_bib = self.parse_asterixes(line.text());
            lines.append(line_with_bib);
            words.append(self.get_words(line_with_bib))
        self.set_word_count(words);
        return lines;
    
    def parse_asterixes(self, text: str):
        return re.sub(r'([*])\1+', lambda match: 'beep' + match.group()[4:] if len(match.group()) > 3 else match.group(), text);
            
    def start_reader(self):
        self.reading_timer = threading.Thread(target=self.shift_word, daemon=True);
        self.reading_timer.start();

    def shift_word(self):
        lines = len(self.word_matches);
        word_number = 0;
        while not self.use_tts and lines > self.line_number:
            if len(self.word_matches[self.line_number]) > word_number:
                word = self.word_matches[self.line_number][word_number];
                s = self.seconds_spent_on_word(word.value);
                self.on_word(None, word.start, len(word.value), False)
                word_number += 1
                sleep(s);
            else:
                self.on_word(None, None, None, True)
                self.update_text_view(None, self.line_number + 2)
                word_number = 0;
        if not self.use_tts:
            self.on_read_completion();
    
    def get_words(self, line: str):
        number = r'[+-]?([0-9]+[.])?[0-9]+';
        text = r'([a-zA-ZäöüæøåßÄÖÜÆØÅ]+[\'’`-])?[a-zA-ZäöüæøåßÄÖÜÆØÅ]+[\.?!,]?';
        word = '(('+number+')|('+text+'))';
        return [WordMatch(x) for x in re.finditer(word, line)];

    def seconds_spent_on_word(self, word: str):
        words_per_minute = self.tts_reader.get_rate();
        word_buffer = 5;
        total = self.number_of_words * word_buffer + self.number_of_characters;
        fraction = (len(word) + word_buffer * self.get_word_weight(word)) / total;
        total_seconds = self.number_of_words / words_per_minute * 60;
        return total_seconds * fraction;

    def set_word_count(self, words: list[list[WordMatch]]):
        self.word_matches = words;
        self.number_of_characters = 0;
        self.number_of_words = 0;
        for wordList in words:
            for word in wordList:
                self.number_of_words += self.get_word_weight(word.value);
                self.number_of_characters += len(word.value);
    
    def get_word_weight(self, word: str):
        match word[-1]:
            case '.': return 3;
            case '?': return 3;
            case '!': return 3;
            case ',': return 2;
            case _: return 1;

    def read_manga(self, result: ScraperResult):
        story, key = self.scrape_service.get_story();
        self.element.find_first('#rdr_lbl_title').text = result.titles.chapter;
        if story or result.titles.story:
            self.element.find_first('#rdr_lbl_story_title').text = story and story.get('name') or result.titles.story or key;
        self.call_javascript('replaceManga', [result.images]);
        self.set_urls();
        self.call_javascript('scrollTo', [f'#manga-page-0', 'auto', 'start']);
        progress = f'(?/{len(result.images)})';
        self.element.find_first('#rdr_lbl_progress').text = progress;
        self.scrape_service.try_to_save(ReadingStatus.READING);

    @sciter.script('get_urls')
    def get_urls(self):
        urls = self.scrape_service.get_urls();
        return {'prev': urls[0], 'current': urls[1], 'next': urls[2], 'list': urls[3]};

    def set_urls(self):
        self.call_javascript('setUrls', [self.get_urls()]);

    def on_read_completion(self):
        self.scrape_service.try_to_save(ReadingStatus.COMPLETED);
        if self.auto_continuation:
            if len(self.html_list) > self.html_index + 1:
                self.html_index += 1;
                self.read_html(self.html_list[self.html_index])
            else:
                self.read(dir=1, force=True);

    def setup_chapter(self, result: ScraperResult):
        self.chapter = {};
        self.append_numeric_lines(result);
        TextHelper.setup_chapter(result, self.parser);
        # print(result.chapter.html);
        self.call_javascript('replaceId', ['rdr_content', result.chapter.html]);

    def print_non_line_content(self, result: ScraperResult):
        forprint = HTMLParser(result.chapter.html);
        lines = forprint.css('.line');
        for line in lines:
            line.remove();
        print(forprint.html);

    def get_children(self, node: Node) -> list[Node]:
        children = [];
        child = node.child;
        while child:
            children.append(child);
            child = child.next;
        return children;
    
    def append_numeric_lines(self, result: ScraperResult):
        for idx, line in enumerate(result.lines):
            if not line.parent:
                print(f'line {idx}: has no parent, {str(line)}');
                continue;
            existing = result.chapter.css_first(f'#line-{idx:05}');
            if existing:
                self.chapter[f"{idx:05}"] = existing;
                continue;
            if line.tag not in ['em', 'strong', 'small', 'b', 'big', 'span', '-text']:
                children = self.get_children(line);
                innerContent = "".join(x.html for x in children);
                span = HTMLParser(f'<span id="{f"line-{idx:05}"}" class="line" title="{f"line-{idx:05}"}">{innerContent}</span>').body.child;
                if line.last_child:
                    line.last_child.insert_after(span);
                    for child in children:
                        child.remove();
                self.chapter[f"{idx:05}"] = span;
                continue;
            content = line.html
            span = HTMLParser(f'<span id="{f"line-{idx:05}"}" class="line" title="{f"line-{idx:05}"}">{content}</span>').body.child;
            line.insert_after(span);
            line.remove();
            self.chapter[f"{idx:05}"] = span;
    
    def skip_line(self):
        count = self.tts_reader.skip_line() - 1;
        currentLine = self.chapter[f"{count:05}"].text();
        dimmed = f'<span style="background-color:#434343;color:#dbdbdb">{currentLine}</span>';
        self.call_javascript('replaceId', [f"line-{count:05}", dimmed]);
        return sciter.Value.null();

    @sciter.script('goto_line')
    def goto_line(self, start: str):
        if self.chapter[start]:
            lines = [];
            start_int = int(start)
            count = start_int;
            while f"{count:05}" in self.chapter:
                lines.append(self.chapter[f"{count:05}"].text());
                count += 1;
            self.tts_reader.set_queue(start_int, lines);
        return sciter.Value.null();

    def paste(self):
        return pc.paste();

    @sciter.script('paste_html')
    def paste_html(self):
        text = pc.paste();
        return text;

    @sciter.script('read_paste')
    def read_paste(self):
        self.read_html(self.paste_html());
        pass

    def Object(self, **kwargs):
        return type("Object", (), kwargs);

    @sciter.script('read_html')
    def read_html(self, html: str):
        body = HTMLParser(f'<div>{html}</div>').body.child;
        result = ScraperResult(
            story_type=StoryType.NOVEL,
            urls = UrlResult(prev=None, current = None, next=None),
            chapter = body,
            lines = None,
            titles = KeyResult(story=None, chapter='Pasted content', domain=None),
            keys = KeyResult(story=None, chapter=None, domain=None),
        );
        self.read_tts(result=result, force=True);

    @sciter.script('read_html_list')
    def read_html_list(self, html_list: list[str]):
        self.html_list = html_list;
        self.html_index = 0;
        self.read_html(html_list[self.html_index]);

    @sciter.script('copy_url')
    def copy_url(self, dir = 0):
        urls = self.scrape_service.get_urls();
        pc.copy(urls[dir + 1]);
        return sciter.Value.null();

    def toggle_driver(self, result):
        self.driver.toggle(result);
        return result;
        
    @sciter.script('copy_text')
    def copy_text(self, text: str):
        pc.copy(text);
        return sciter.Value.null();

    @sciter.script('copy_content')
    def copy_content(self):
        pc.copy(self.scrape_service.result);
        return sciter.Value.null();

    @sciter.script('open_link')   
    def open_link(self, link: str):
        webbrowser.open(link, new=2);
        return sciter.Value.null();

    @sciter.script('toggle_auto')
    def toggle_auto(self):
        self.auto_continuation = not self.auto_continuation;
        return self.auto_continuation;

    @sciter.script('toggle_scroll')
    def toggle_scroll(self):
        self.auto_scroll = not self.auto_scroll;
        return self.auto_scroll;

    @sciter.script('pause')
    def pause(self):
        self.tts_reader.toggle_pause(pause_callback=self.set_pause_label);
        return sciter.Value.null();

    def next_voice(self):
        voice = self.tts_reader.next_voice();
        return voice;

    @sciter.script('set_voice') 
    def set_voice(self, voice: str):
        self.tts_reader.set_voice(voice);
        return sciter.Value.null();

    @sciter.script('next_rate')
    def next_rate(self):
        rate = self.tts_reader.next_rate();
        return rate;

    @sciter.script('set_tts')
    def set_tts(self):
        self.use_tts = not self.use_tts;
        return self.use_tts;
        
    def on_word(self, name: str, location: int = 0, length: int = 0, completed: Optional[bool] = None):
        if not f"{self.line_number:05}" in self.chapter:
            print(f'chapter does not have {self.line_number:05}');
            return;
        current_node = self.chapter[f"{self.line_number:05}"];
        current_line = htmlParser.unescape(current_node.html);
        if not length and (completed is not None):
            self.call_javascript('replaceId', [f"line-{self.line_number:05}", self.chapter[f"{self.line_number:05}"].html[len(self.get_line_prefix()):-7]]);
            return;
        word_end = len(self.get_line_prefix()) + location + length;
        word = current_line[word_end-length:word_end];
        highlighted = f'{htmlParser.escape(current_line[len(self.get_line_prefix()):word_end-length])}<span style="background-color:#555;color:#f1f1f1">{htmlParser.escape(word)}</span>{htmlParser.escape(current_line[word_end:-7])}';
        if self.element:
            self.call_javascript('replaceId', [f"line-{self.line_number:05}", highlighted]);

    def set_pause_label(self, pause: bool):
        self.element.find_first('#rdr_btn_pause').text = 'Resume' if pause else 'Pause';

    def update_text_view(self, _, count: int):
        self.line_number = count - 1;
        progress = f'({count}/{len(self.chapter)})';
        self.element.find_first('#rdr_lbl_progress').text = progress;
        if self.line_number == 0:
            self.call_javascript('scrollLineToTop', [self.line_number]);
        if self.auto_scroll and self.chapter.get(f"{self.line_number:05}"):
            self.scroll();

    def scroll(self):
        self.call_javascript('scrollLineToCenter', [self.line_number]);
        # self.call_javascript('scrollToCenterOf', [f'#line-{self.line_number:05}']);

    def get_line_prefix(self):
        return f'<span id="line-{self.line_number:05}" class="line" title="line-{self.line_number:05}">';
