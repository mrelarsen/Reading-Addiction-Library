import requests;
import random;

class Joke():
    def __init__(self, joke_type=None):
        joke_type = joke_type or random.randrange(10);
        self.texts = ['None'];
        self.type = 'None';
        if joke_type == 0:
            self.type = 'Geek joke';
            self.texts = self.get_geek_joke();
        elif joke_type == 1:
            self.type = 'Programming joke';
            self.texts = self.get_programming_joke();
        elif joke_type == 2:
            self.type = 'Miscellaneous joke';
            self.texts = self.get_misc_joke();
        elif joke_type == 3:
            self.type = 'Dark joke';
            self.texts = self.get_dark_joke();
        elif joke_type == 4:
            self.type = 'Pun joke';
            self.texts = self.get_pun_joke();
        elif joke_type == 5:
            self.type = 'Spooky joke';
            self.texts = self.get_spooky_joke();
        elif joke_type == 6:
            self.type = 'Christmas joke';
            self.texts = self.get_christmas_joke();
        elif joke_type == 7:
            self.type = 'Ron Swanson quote';
            self.texts = self.get_ron_swanson_quote();
        elif joke_type == 8:
            self.type = 'Chuck Norris fact';
            self.texts = self.get_chuck_norris_fact();
        elif joke_type == 9:
            self.type = 'Dad joke';
            self.texts = self.get_dad_joke();
        
    def get_geek_joke(self):
        response = requests.get('https://geek-jokes.sameerkumar.website/api');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_question(json);

    def get_programming_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Programming');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
    def get_misc_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Miscellaneous');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
    def get_dark_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Dark');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
    def get_pun_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Pun');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
    def get_spooky_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Spooky');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
    def get_christmas_joke(self):
        response = requests.get('https://v2.jokeapi.dev/joke/Christmas');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return self.parse_jokeapi_json(json);
        
    def get_ron_swanson_quote(self):
        response = requests.get('https://ron-swanson-quotes.herokuapp.com/v2/quotes');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json();
        else:
            return(['Something went wrong, not json response']);
        return json;

    def get_chuck_norris_fact(self):
        response = requests.get('https://api.chucknorris.io/jokes/random');
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json()['value'];
        else:
            return(['Something went wrong, not json response']);
        return self.parse_question(json);

    def get_dad_joke(self):
        response = requests.get('https://icanhazdadjoke.com/', headers={'accept': 'application/json'});
        if 'application/json' in response.headers.get('Content-Type', ''):
            json = response.json()['joke'];
        else:
            return(['Something went wrong, not json response']);
        return self.parse_question(json);

    def parse_jokeapi_json(self, json):
        if 'type' in json and json['type'] == 'twopart':
            setup = json['setup'];
            delivery = json['delivery']
            return [setup, '...', '...', delivery];
        elif 'type' in json and json['type'] == 'single':
            return [json['joke']];
        elif 'joke' in json:
            return [json['joke']];
        else:
            print(json.__dict__)
            return(['Something went wrong']);

    def parse_question(self, text):
        if not isinstance(text, str):
            print('Error parsing joke', text);
            return ['Error parsing joke'];
        arr = text.split('?');
        if len(arr) == 2:
            return [arr[0], '...', '...', arr[1]];
        return [text];