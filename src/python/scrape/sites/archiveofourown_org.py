import os;
import re;
import requests
import html as htmlEncoder;
from selectolax.parser import Node
from models.driver import Driver;
from scrape.configure_site_scraper import ConfigureSiteScraper;

class SiteScraper(ConfigureSiteScraper):
    def __init__(self, url, driver: Driver, session_dict: dict[str, requests.Session]):
        self._setup_folders();
        self._set_strings();
        super().useHtml(url);
    
    def getConfiguration(self, url):
        return None;

    def _set_strings(self):
        self._get_file_name = lambda title: "_".join(x for x in re.split(r'[\\,. "\'/*?:"<>|]', title) if bool(x))
        self._get_new_file_name = lambda file_name: f'archiveofourown_org__{file_name}'
        self._get_html_path = lambda filename: f'{self._html_download_path}/{filename}.html'
        pass
        
    def _scrape(self, node: Node):
        html_path = None;
        try:
            print(f"bob a.a")
            story = node.css_first('.header .heading a');
            story_title = htmlEncoder.escape(story.text());
            story_key = story.attributes['href'].split('/')[-1];
            story_title_url = f'https://archiveofourown.org/downloads/{story_key}/{story_title}.html'
            file_name = self._get_file_name(story.text());
            new_file_name = self._get_new_file_name(file_name);
            html_path = self._get_html_path(new_file_name);
            if not os.path.exists(html_path):
                print(f"starting download, {story_title_url}")
                page = requests.get(story_title_url);
                print(f'saving to file {html_path}')
                self._save(page.content, html_path);
        except Exception as error:
            print('error', error);
            return self._get_default_tts(
                ['An error occurred downloading!', 'Url:', self._url, 'Error:', str(error)],
                'An error occurred downloading!',
                self._url
            );

        if os.path.exists(html_path):
            abs_path = os.path.abspath(html_path);
            return self._get_default_tts(
                ['Fan-fiction has been downloaded', 'Proceeding to file'],
                'Fan-fiction has been downloaded!',
                url = self._url,
                next_url = f'file:///{abs_path}#chap_1',
            );
        else:
            return self._get_default_tts(
                ['Fan-fiction has been downloaded', f'Error: File not found - {html_path}'],
                'Fan-fiction has been downloaded, but an error occurred!',
                self._url
            );
        
    def _save(self, content, dest_dir):
        with open(dest_dir, "wb") as f:
            f.write(content);
        pass