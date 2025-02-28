import os;
import zipfile
import requests
from helpers.story_type import StoryType
from scrape.basic_scraper import ScraperResult;
from helpers.driver import Driver;
from scrape.basic_site_scraper import BasicSiteScraper;
from libraries.fichub.fichub import FicHub
from libraries.fichub.processing import check_url, get_format_type

def get_story_type(sections) -> StoryType:
    return StoryType.NOVEL;

class SiteScraper(BasicSiteScraper):
    def __init__(self, url: str, driver: Driver, session_dict: dict[str, requests.Session], headers: dict[str, str]):
        if not driver.is_running():
            self._result = ScraperResult._get_driver_required(url, get_story_type(None));
        else:
            self._setup_folders();
            self._set_strings();
            super().__init__(url=url, driver=driver.get(), headers=headers);

    def _handle(self, _, __, ___, ____):
        self._result = self._scrape(None, None, None)

    def _set_strings(self):
        self._get_file_name = lambda file_name: f'{os.path.splitext(file_name)[0]}'
        self._get_new_file_name = lambda file_name: f'fanfiction_net__{os.path.splitext(file_name)[0]}'
        self._get_zip_path = lambda filename: f'{self._zip_download_path}/{filename}.zip'
        self._get_html_path = lambda filename: f'{self._html_download_path}/{filename}.html'
        pass
        
    def _scrape(self, _, __, ___):
        supported_url, exit_status = check_url(self._url, False, 0)
        fic = None
        html_file_name = None;
        if supported_url:
            try:
                fic = FicHub(False, False, exit_status);
                fic.get_fic_metadata(self._url, get_format_type("html"));

                file_name = self._get_file_name(fic.file_name);
                new_file_name = self._get_new_file_name(fic.file_name);

                zip_file_name = self._get_zip_path(new_file_name);
                if not os.path.exists(zip_file_name):
                    fic.get_fic_data(fic.download_url);
                    self._zip(fic.response_data.content, zip_file_name);
                    
                html_file_name = self._get_html_path(new_file_name);
                if not os.path.exists(html_file_name):
                    abs_zip_file_name = os.path.abspath(zip_file_name);
                    abs_html_download_path = os.path.abspath(self._html_download_path);
                    self._unzip(abs_zip_file_name, abs_html_download_path, file_name);
                print('downloaded')

            except Exception as error:
                return ScraperResult._get_default_tts(
                    texts = ['An error occurred downloading!', 'Url:', self._url, 'Error:', str(error)],
                    title = 'An error occurred downloading!',
                    url = self._url);
        else:
            return ScraperResult._get_default_tts(
                texts = ['The url is unsupported!', 'Url:', self._url],
                title = 'The url is unsupported!',
                url = self._url);

        abs_path = os.path.abspath(html_file_name);
        if os.path.exists(abs_path):
            return ScraperResult._get_default_tts(
                texts = ['Fan-fiction has been downloaded', 'Proceeding to file'],
                title = 'Fan-fiction has been downloaded!',
                url = self._url,
                next_url = f'file:///{abs_path}#chap_1',
                loading = True);
        else:
            return ScraperResult._get_default_tts(
                texts = ['Fan-fiction has been downloaded', f'Error: File not found - {abs_path}'],
                title = 'Fan-fiction has been downloaded, but an error occurred!',
                url = self._url);
        # e.g.file:///C:/Reading-Addiction-Library/Python/html/The_Queen_who_fell_to_Earth_by_Bobmin356-dwmB626w.html#chap_1'
        
    def _zip(self, content: bytes, dest_dir: str):
        with open(dest_dir, "wb") as f:
            f.write(content);
        pass
        
    def _unzip(self, source_filename: str, dest_dir: str, name: str):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir);
            os.rename(f'{dest_dir}\\{name}.html', f'{dest_dir}\\fanfiction_net__{name}.html');
        pass