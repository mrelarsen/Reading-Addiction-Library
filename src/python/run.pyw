import json
import os
import run_paths;
import sciter
from handlers.reader_section import ReaderEventHandler
from helpers.driver import Driver
from database.history import History
from handlers.story_section import StoryEventHandler

class Window(sciter.Window):
    def __init__(self):
        super().__init__(ismain=True, uni_theme=True, debug=True)
        self.set_dispatch_options(enable=True, require_attribute=False)
        self.settings = self.load_settings();
        self.history = History(self.settings.get('database_path'));
        self.tab_content = None;
        self.driver = Driver(self.call_javascript);

        self.reader_section = None;
        self.reader_handler = None;
        self.story_section = None;
        self.story_handler = None;
        pass
    
    @sciter.script('save_settings')
    def save_settings(self, settings: dict):
        json_string = json.dumps({
            "auto_continuation": settings.get('auto_continuation'),
            "auto_scroll": settings.get('auto_scroll'),
            "use_tts": settings.get('use_tts'),
            "text_size": settings.get('text_size'),
            "rate": settings.get('rate'),
            "voice": settings.get('voice'),
            "volume": settings.get('volume'),
            "database_path": self.settings.get('database_path'),
        });
        with open('./settings.json', "wt") as f:
            f.write(json_string);
        self.reader_handler.set_settings(settings);

    def load_settings(self) -> dict:
        settings = {
            "auto_continuation": True,
            "auto_scroll": True,
            "use_tts": True,
            "text_size": 1,
            "rate": 400,
            "volume": 1,
            "voice": 'zira',
            "database_path": './database/stories.db',
        }
        if os.path.exists('./settings.json'):
            with open('./settings.json', "r") as f:
                content = f.read();
                json_dict: dict = json.loads(content);
                for key, value in json_dict.items():
                    settings[key] = value;
        return settings;

    def on_data_loaded(self, nm):
        # loaded
        if self.get_root():
            if not self.reader_section:
                reader = self.get_root().find_first('#reader_section');
                if reader:
                    self.reader_section = reader;
                    self.reader_handler = ReaderEventHandler(reader, self.settings, self.history, self.call_javascript, self.driver);
            if not self.story_section:
                story = self.get_root().find_first('#story_section');
                if story:
                    self.story_section = story;
                    self.story_handler = StoryEventHandler(story, self.history, self.call_javascript);
        pass

    @sciter.script('call_handler')
    def call_handler(self, handlerName: str, method: str, params: list):
        handler = getattr(self, handlerName)
        return getattr(handler, method)(*params)

    @sciter.script('shutdown')
    def shutdown(self):
        self.driver.toggle(False);

    def call_javascript(self, methodName: str, params: list):
        try:
            self.call_function(methodName, *params)
        except Exception as e:
            print(f'{methodName} was not found as a global function')
            print(str(e))
            print(*params)

    def check(self, fn):
        def c():pass
        for item in globals().keys():
            if type(globals()[item]) == type(c) and fn == item:
                return print(item, "is Function!")
            elif fn == item:
                return print(fn, "is", type(globals()[item]))
        return print("Can't find", fn)

if __name__ == "__main__":
    print("Sciter version:", sciter.version(as_str=True))

    # create window
    frame = Window()

    # enable debug only for this window
    frame.setup_debug()

    # load file
    frame.load_file("../javascript/run.htm")

    frame.run_app()
