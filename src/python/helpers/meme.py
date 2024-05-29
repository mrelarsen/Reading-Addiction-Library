import random
import requests;

class Meme():
    def __init__(self, meme_type: str|None = None):
        meme_types = ['memes', 'dankmemes', 'me_irl', 'wholesomememes'];
        meme_type = meme_type or meme_types[random.randrange(len(meme_types))];
        response = requests.get(f'https://meme-api.com/gimme/{meme_type}');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
            self.title = json['title'];
            response = requests.get(json['url']);
            img_type = response.headers["Content-Type"].split("/")[-1];
            if img_type != 'error':
                self.images = [response.content];
                self.texts = [];
            else:
                self.texts = ['Error fetching mime image'];
                self.images = None;
        else:
            self.title = 'Error fetching mime';
            self.texts = ['Error fetching mime'];
            self.images = None;