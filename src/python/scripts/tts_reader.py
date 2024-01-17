import threading;
import os;
import queue;
from typing import Any;
from libraries.pyttsx3_custom import engineInit;

class TTSReader():
    def __init__(self, settings=None, word_callback = None):
        self.__queue = queue.Queue();
        self.__pause = False;
        self.__t = None;
        self.__count = 0;
        self.__settings = settings;
        self.chapter_callback = None;
        self.update_callback = None;
        self.__word_callback = word_callback;
        self.__init_pyttsx3(settings, word_callback);
        
    def __init_pyttsx3(self, settings:dict[str, Any]=None, word_callback = None):
        self.__engine=engineInit(debug=True);
        if word_callback:
            self.__engine.connect('started-word', word_callback)
            self.__engine.connect('finished-utterance', word_callback)
        self.__voices = self.__engine.getProperty('voices');
        self.__rates = [400, 425, 450, 475, 500];
        if settings:
            self.set_settings(settings);
        else:
            self.set_voice('zira');
            self.set_rate(400);
            self.set_volume(1);
    
    def reset_pyttsx3(self):
        self.__engine.stop();
        self.__init_pyttsx3(self.__settings, self.__word_callback);

    def set_settings(self, settings:dict[str, Any]):
        self.__settings = settings;
        voice = settings.get('voice');
        rate = settings.get('rate');
        volume = settings.get('volume');
        self.set_voice(voice);
        self.set_rate(rate);
        self.set_volume(volume);


    def get_volume(self):
        return self.__engine.getProperty('volume');
    def get_rate(self):
        return self.__rates[self.__rate_index]/100;
    def get_voice(self):
        return self.__voices[self.__voice_index].name;
    def get_voices(self):
        return list(map(lambda x: x.name, self.__voices));
        
    def set_volume(self, volume):
        self.__engine.setProperty('volume', volume);

    def set_rate(self, rate):
        if rate in self.__rates:
            self.__rate_index = self.__rates.index(rate);
        else:
            self.__rate_index = 0;
        self.__engine.setProperty('rate', self.__rates[self.__rate_index]);
        
    def set_voice(self, voiceName):
        voice = next((x for x in self.__voices if voiceName in x.name.lower()));
        self.__voice_index = self.__voices.index(voice) or 0;
        self.__engine.setProperty('voice', self.__voices[self.__voice_index].id);

    def next_voice(self):
        self.__voice_index = (self.__voice_index + 1) % len(self.__voices);
        self.__engine.setProperty('voice', self.__voices[self.__voice_index].id);
        return self.__voices[self.__voice_index].name;

    def next_rate(self):
        self.__rate_index = (self.__rate_index + 1) % len(self.__rates);
        self.__engine.setProperty('rate', self.__rates[self.__rate_index]);
        return self.__rates[self.__rate_index]/100;

    def toggle_pause(self, pause_callback = None):
        self.__pause = self.__engine.toggle_pause();
        if pause_callback:
            pause_callback(self.__pause);
        if not self.__pause and not self.__queue.empty():
            if self.__t == None or not self.__t.is_alive():
                self.__run_thread();

    def skip_line(self):
        if not self.__queue.empty():
            self.__queue.get();
            self.__count += 1;
            return self.__count;

    def download(self, text, save_path, file_name):
        download_path = os.path.abspath(save_path);
        if not os.path.exists(download_path):
            os.makedirs(download_path); 
        abs_path = os.path.abspath(save_path + file_name + '.wav');
        if self.__t:
            self.__t.join();
        self.__t = threading.Thread(target=self.download_async, args=(text, abs_path,), daemon=True);
        self.__t.start();

    def download_async(self, text, file):
        print(f'"{text[:10]}"', file)
        self.__engine.save_to_file(text, file);
        self.__engine.runAndWait();
        print('completed download of', file.split('\\')[-1])
    
    def read(self, lines = None, force = False, update_callback = None, completed_callback = None):
        if not lines or len(lines) == 0: return;
        self.update_callback = update_callback;
        self.completed_callback = completed_callback;
        self.set_queue(0, lines);
        if self.__t == None or not self.__t.is_alive() or force:
            self.__run_thread();
    
    def set_queue(self, start, lines):
        self.__count = start;
        self.__pause = False;
        with self.__queue.mutex:
            self.__queue.queue.clear();
        for line in lines:
            self.__queue.put(str(line).replace('<', '{').replace('>','}'))

    def __run_thread(self):
        self.__t = threading.Thread(target=self.__run_line, args=(self.__queue.get(),), daemon=True);
        self.__t.start();

    def __update(self, text):
        self.__count += 1;
        if self.update_callback:
            self.update_callback(text, self.__count);

    def __run_line(self, text):
        self.__update(text);
        self.__run_pyttsx3(text);
        
        if not self.__queue.empty():
            if not self.__pause:
                self.__run_thread();
        elif self.completed_callback:
            self.completed_callback();

    def __run_pyttsx3(self, text):
        self.__engine.say(text);
        self.__engine.runAndWait();
