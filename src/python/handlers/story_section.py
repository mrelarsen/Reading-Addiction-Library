import pyperclip as pc
import sciter
from database.history import History
from typing import Any, Callable

class StoryEventHandler(sciter.EventHandler):
    def __init__(self, el, history: History, call_javascript: Callable[[str, Any], None]):
        super().__init__(element=el)
        self.history = history;
        self.chapters = None;
        self.call_javascript = call_javascript;
        pass
        
    @sciter.script('save_chapter_details')
    def save_chapter_details(self, chapter_id, chapter_name, chapter_desc, chapter_status):
        return self.history.save_chapter_details(chapter_id, chapter_name, chapter_desc, chapter_status);
        
    @sciter.script('save_story_details')
    def save_story_details(self, story_id, story_name, story_desc, story_rating = '0.0', tags = ''):
        return self.history.save_story_details(story_id, story_name, story_desc, float(story_rating), tags);

    @sciter.script('get_stories')
    def get_stories(self, term = None):
        self.stories = self.history.get_stories(term);
        return self.stories;

    @sciter.script('get_story')
    def get_story(self, story_id):
        return self.history.get_story(story_id, None, None);

    @sciter.script('get_chapter')
    def get_chapter(self, chapter_id):
        return self.history.get_chapter(chapter_id);

    @sciter.script('get_chapters')
    def get_chapters(self, story_id):
        self.chapters = self.history.get_chapters(story_id);
        return self.chapters;

    @sciter.script('read_summaries')
    def read_summaries(self, story_id):
        chapters = self.history.get_chapters(story_id);
        summaries = filter(lambda summary: bool(summary.strip()), map(lambda chapter: chapter['desc'], chapters));
        pass

    @sciter.script('copy_chapter_url')
    def copy_chapter_url(self, chapter_id):
        chapter = self.history.get_chapter(chapter_id);
        pc.copy(chapter['url']);
        pass

    @sciter.script('merge_stories')
    def merge_stories(self, story_ids: list[int]):
        story_ids.sort();
        from_ids = story_ids[1:];
        to_id = story_ids[0];
        print(f'Merge stories {from_ids} into {to_id}');
        self.history.merge_stories(from_ids, to_id);
        story = self.history.get_story(to_id);
        return [from_ids, story];

    @sciter.script('merge_database')
    def merge_database(self, file_name):
        print(f'Merge database: {file_name}');
        self.history.merge_database(file_name);
        print(f'Done merging!');
        pass
