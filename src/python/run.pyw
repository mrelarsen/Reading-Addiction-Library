import run_paths;
import sciter
from handlers.reader_section import ReaderEventHandler
from models.driver import Driver
from database.history import History
from handlers.story_section import StoryEventHandler

class Window(sciter.Window):
    def __init__(self):
        super().__init__(ismain=True, uni_theme=True, debug=True)
        self.set_dispatch_options(enable=True, require_attribute=False)
        self.history = History();
        self.tab_content = None;
        self.driver = Driver(self.call_javascript);

        self.reader_section = None;
        self.reader_handler = None;
        self.story_section = None;
        self.story_handler = None;
        pass

    def on_data_loaded(self, nm):
        # loaded
        if self.get_root():
            if not self.reader_section:
                reader = self.get_root().find_first('#reader_section');
                if reader:
                    self.reader_section = reader;
                    self.reader_handler = ReaderEventHandler(reader, self.history, self.call_javascript, self.driver);
            if not self.story_section:
                story = self.get_root().find_first('#story_section');
                if story:
                    self.story_section = story;
                    self.story_handler = StoryEventHandler(story, self.history, self.call_javascript);
        pass

    @sciter.script('call_handler')
    def call_handler(self, handlerName, method, params):
        handler = getattr(self, handlerName)
        return getattr(handler, method)(*params)

    @sciter.script('shutdown')
    def shutdown(self):
        self.driver.toggle(False);

    def call_javascript(self, methodName: str, params):
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
