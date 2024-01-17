import html as htmlParser;
import importlib
import json;
import os
import pyperclip as pc;
import re;
import sciter;
import webbrowser
from database.history import History
from models.driver import Driver
from models.reading_status import ReadingStatus
from models.story_type import StoryType;
from selectolax.parser import HTMLParser, Node
from scripts.text_helper import TextHelper;
from scrape.basic_scraper import ScraperResult;
from scripts.scrape_service import ScrapeService
from scripts.tts_reader import TTSReader
from time import sleep
from typing import Any, Callable

cssutils_spec = importlib.util.find_spec("cssutils")
if cssutils_spec:
    from cssutils import CSSParser

class ReaderEventHandler():
    def __init__(self, el: sciter.dom.Element, history: History, call_javascript: Callable[[str, list[Any]], None], driver: Driver):
        settings = self.load_settings();
        self.element=el;
        self.history = history;
        self.driver: Driver = driver;
        self.selector = '#rdr_content';
        self.word_callback = self.on_word;
        self.scrape_service = ScrapeService(self.history, self.driver);
        self.tts_reader = TTSReader(settings=settings, word_callback=self.word_callback);
        self.auto_scroll = settings and settings.get('auto_scroll') or True;
        self.line = None;
        self.line_prefix = '<div style="padding-left:3px;padding-right:3px">';
        self.auto_continuation = settings and settings.get('auto_continuation') or True;
        self.chapter: dict[str, Node] = {};
        self.line_number = 0;
        self.call_javascript = call_javascript;
        self.text_size = settings and settings.get('text_size') or 1;
        self.parser = None;
        if cssutils_spec:
            self.parser = CSSParser();
        pass
    

    @sciter.script('save_settings')
    def save_settings(self, settings: dict):
        json_string = json.dumps({
            "auto_continuation": settings.get('auto_continuation'),
            "auto_scroll": settings.get('auto_scroll'),
            "text_size": settings.get('text_size'),
            "rate": settings.get('rate'),
            "voice": settings.get('voice'),
            "volume": settings.get('volume'),
        });
        with open('./settings.json', "wb") as f:
            f.write(json_string);
        self.tts_reader.set_settings(settings);

    def load_settings(self) -> dict:
        json_dict = None
        if os.path.exists('./settings.json'):
            with open('./settings.json', "r") as f:
                content = f.read();
                json_dict = json.loads(content);
        return json_dict;

    @sciter.script('get_settings')
    def get_settings(self) -> dict:
        return {
            "auto_continuation": self.auto_continuation,
            "auto_scroll": self.auto_scroll,
            "driver": self.driver.is_running(),
            "text_size": self.text_size,
            "rate": self.tts_reader.get_rate(),
            "volume": self.tts_reader.get_volume(),
            "voice": self.tts_reader.get_voice(),
            "voices": self.tts_reader.get_voices(),
        };

    @sciter.script('reset_reader')
    def reset_reader(self):
        self.tts_reader.reset_pyttsx3();

    @sciter.script('read_list')
    def read_list(self, text):
        urllist = [x for x in re.split(r'[\s,]', text) if x and (x.startswith('http') or x.startswith('file'))];
        print(urllist)
        self.read(urllist=urllist);
        pass

    @sciter.script('download_list')
    def download_list(self, text):
        urllist = [x for x in re.split(r'[\s,]', text) if x];
        print(urllist)
        if urllist[0].isdigit():
            self.download(amount=int(urllist[0]), urllist=urllist[1:]);
        else:
            self.download(urllist=urllist);
        pass

    def download(self, amount = 0, urllist = None):
        for i in range(len(urllist)):
            result = self.download_chapter(urllist[i]);
            counter = 1;
            while result and result.urls.next and counter < amount:
                result = self.download_chapter(result.urls.next);
                counter += 1;
        print('Done downloading!');

    def download_chapter(self, url):
        _, result = self.scrape_service.read_info(url=url, buffer=False, loading=False);
        while result.is_loading():
            sleep(0.5);
            _, result = self.scrape_service.read_info(url=url, buffer=False, loading=False);
        sections = [x for x in re.split(r'[/.-]', result.keys.story) if x];
        abbreviation = "".join(map(lambda x: x[0], sections)) if len(sections) > 1 else result.keys.story;
        chapter_id = self.scrape_service.try_to_save(ReadingStatus.DOWNLOADED);
        title = "-".join(x for x in re.split(r'[\s/.,:-]', result.title) if x);
        text = result.chapter.text(deep=True, strip=True);
        self.tts_reader.download(text=text, save_path='downloads/wavs/', file_name=f'{abbreviation}-{chapter_id}-{title}');
        return result;
        # self.tts_reader.download(text=pc.paste(), save_path='downloads/wavs/', file_name=f'hello');

    @sciter.script('read')
    def read(self, dir = 0, force = False, urllist = None):
        story_type, result = self.scrape_service.read_info(dir=dir, urllist=urllist);
        if story_type == StoryType.NOVEL:
            print('novel')
            self.read_tts(result=result, force=force);
        elif story_type == StoryType.MANGA:
            print('manga')
            self.read_manga(result=result);
        else:
            print('Url not found or wrong format!');

    def read_tts(self, result: ScraperResult, force):
        TextHelper.clean_html(result, self.parser);
        lines = [];
        for idx, line in enumerate(result.lines):
            line_with_bib = self.parse_asterixes(line.text());
            lines.append(line_with_bib);
        self.setup_chapter(result);
        self.tts_reader.read(lines=lines, force=force, update_callback=self.update_text_view, completed_callback=self.on_read_completion)
        self.element.find_first('#rdr_lbl_title').text = result.title;
        if result.domain:
            story, key = self.scrape_service.get_story();
            if story:
                self.element.find_first('#rdr_lbl_story_title').text = story and story.get('name') or key;
            self.set_urls();
            self.scrape_service.try_to_save(ReadingStatus.READING);
        self.lineNumber = 0;
        self.scroll();
    
    def parse_asterixes(self, text:str):
        return re.sub(r'([*])\1+', lambda match: 'beep' + match.group()[4:] if len(match.group()) > 3 else match.group(), text);

    def read_manga(self, result: ScraperResult):
        story, key = self.scrape_service.get_story();
        self.element.find_first('#rdr_lbl_title').text = result.title;
        if story:
            self.element.find_first('#rdr_lbl_story_title').text = story and story.get('name') or key;
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
            self.read(dir=1, force=True);

    def setup_chapter(self, result: ScraperResult):
        self.chapter = {};
        self.append_numeric_lines(result);
        TextHelper.setup_chapter(result, self.parser);
        # print(result.chapter.html);
        self.call_javascript('replaceId', ['rdr_content', result.chapter.html]);
        self.line_number = 0;

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
        if result.chapter:
            for idx, line in enumerate(result.lines):
                if not line.parent:
                    print(f'line {idx}: has no parent, {str(line)}');
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
        else:
            line_contents = map(lambda line: str(line).replace('<', '{').replace('>','}'), result.lines);
            lineList = map(lambda line_content: f'<span id="line-{idx:05}" title="line-{idx:05}">{line_content}</span>', line_contents);
            result.chapter = HTMLParser(f'<div>{"".join(lineList)}</div>').body.child;
            chapterChild = result.chapter.child;
            while chapterChild:
                self.chapter[span['id'][5:]] = span;
                chapterChild = chapterChild.next;
    def skip_line(self):
        count = self.tts_reader.skip_line() - 1;
        currentLine = self.chapter[f"{count:05}"].text();
        dimmed = f'<span style="background-color:#434343;color:#dbdbdb">{currentLine}</span>';
        self.call_javascript('replaceId', [f"line-{count:05}", dimmed]);
        return sciter.Value.null();

    @sciter.script('goto_line')
    def goto_line(self, start):
        if self.chapter[start]:
            lines = [];
            count = int(start);
            while f"{count:05}" in self.chapter:
                lines.append(self.chapter[f"{count:05}"].text());
                count += 1;
            self.tts_reader.set_queue(int(start), lines);
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
    def read_html(self, html):
        body = HTMLParser(html).body;
        result = ScraperResult(
            story_type=StoryType.NOVEL,
            urls = self.Object(prev=None, current = None, next=None),
            chapter = body,
            lines = None,
            title = 'Pasted content',
            keys = self.Object(story=None, chapter=None),
        );
        self.read_tts(result=result, force=False);

    @sciter.script('copy_url')
    def copy_url(self, dir = 0):
        urls = self.scrape_service.get_urls();
        pc.copy(urls[dir + 1]);
        return sciter.Value.null();

    def toggle_driver(self, result):
        self.driver.toggle(result);
        return result;
        
    @sciter.script('copy_text')
    def copy_text(self, text):
        pc.copy(text);
        return sciter.Value.null();

    @sciter.script('copy_content')
    def copy_content(self):
        pc.copy(self.scrape_service.result);
        return sciter.Value.null();

    @sciter.script('open_link')   
    def open_link(self, link):
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
    def set_voice(self, voice):
        self.tts_reader.set_voice(voice);
        return sciter.Value.null();

    @sciter.script('next_rate')
    def next_rate(self):
        rate = self.tts_reader.next_rate();
        return rate;
        
    def get_line(self):
        return f"#line-{self.line_number:05}";

    def on_word(self, name, location = None, length = None, completed = None):
        if not f"{self.line_number:05}" in self.chapter:
            print(f'chapter does not have {self.line_number:05}');
            return;
        current_node = self.chapter[f"{self.line_number:05}"];
        # copy_node = HTMLParser(current_node.html).body.child;
        # copy_node.unwrap_tags(['em', 'strong', 'small', 'b', 'big']);
        current_line = htmlParser.unescape(current_node.html);
        if not length and (completed != None):
            self.call_javascript('replaceId', [f"line-{self.line_number:05}", self.chapter[f"{self.line_number:05}"].html]);
            return;
        word_end = len(self.get_line_prefix()) + location + length;
        word = current_line[word_end-length:word_end];
        highlighted = f'{htmlParser.escape(current_line[len(self.get_line_prefix()):word_end-length])}<span style="background-color:#555;color:#f1f1f1">{htmlParser.escape(word)}</span>{htmlParser.escape(current_line[word_end:-7])}';
        if self.element:
            self.call_javascript('replaceId', [f"line-{self.line_number:05}", highlighted]);

    def set_pause_label(self, pause):
        self.element.find_first('#rdr_btn_pause').text = 'Resume' if pause else 'Pause';

    def reset_reader_content(self):
        self.element.find_first('#rdr_content').clear();
        self.set_pause_label(False);
    
    def update_text_view(self, _, count):
        self.line_number = count - 1;
        progress = f'({count}/{len(self.chapter)})';
        self.element.find_first('#rdr_lbl_progress').text = progress;
        if self.auto_scroll:
            self.scroll();

    def add_content(self, text):
        self.line = f'{self.get_line_prefix()}{text}</div>';
        self.call_javascript('appendOn', ['#rdr_content', self.line]);
    
    def scroll(self):
        self.call_javascript('scrollToCenterOf', [f'#line-{self.line_number:05}']);

    def get_line_prefix(self):
        return f'<span id="line-{self.line_number:05}" class="line" title="line-{self.line_number:05}">';
