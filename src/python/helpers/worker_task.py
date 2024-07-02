import importlib
import os
import re
from helpers.scraper_result import ScraperResult

class WorkerTask():
    def __init__(self, url: str|None = None, urllist: list[str]|None = None, adjecent = False):
        url = url or (urllist and urllist[0]) or '';
        self.url = url if url == '' or url[0] != '!' else url[1:];
        self.urllist = urllist;
        self.adjecent = adjecent;
        self.tries = 0;
        self.module_name, self.alt_url = self.__get_module_name(self.url);
        self.module_class, get_story_type = self.__get_module(self.module_name);
        self.module_story_type = get_story_type(self.url.split('/'));
        pass

    def increment(self):
        self.tries += 1;
    
    def get_ensuing_task_from_list(self, dir: int, result: ScraperResult):
        if self.urllist and not result.is_loading():
            index, url = self.get_match(self.url);
            if url and (url[0] != '!' or dir < 0):
                next_index = dir + index;
                if index != -1 and next_index >= 0 and next_index < len(self.urllist):
                    return WorkerTask(self.urllist[next_index], self.urllist, True);
            elif dir > 0 and url:
                next = None if result is None else result.get_ensuing_url(dir);
                if next:
                    next_index, next_url = self.get_match(next);
                    if next_url:
                        self.urllist.remove(next_url);
                    self.urllist.insert(index + 1, '!' + next);
                    return WorkerTask(next, self.urllist, True);
                else:
                    if index + 1 < len(self.urllist):
                        return WorkerTask(self.urllist[index + 1], self.urllist, True);
        return None;

    def get_ensuing_task_from_result(self, dir: int, result: ScraperResult):
        url = None if result is None else result.get_ensuing_url(dir);
        if url:
            return WorkerTask(url, None, True);
        return None;

    def get_ensuing_task(self, dir: int, result: ScraperResult):
        task = self.get_ensuing_task_from_list(dir, result);
        return task or self.get_ensuing_task_from_result(dir, result);

    def get_match(self, url: str):
        if self.urllist:
            for x in [url, f'!{url}']:
                if x in self.urllist:
                    index = self.urllist.index(x);
                    return index, self.urllist[index];
        return None, None;

    def __get_module_name(self, scrape_url: str):
        if not scrape_url: return (None, None);
        if scrape_url.startswith("file"):
            url = ''
            if scrape_url.startswith("file:///"): url = scrape_url[8:];
            elif scrape_url.startswith("file://"): url = scrape_url[7:];
            modulename = '';
            route_head = re.split(r'[\\/]', scrape_url)[-1];
            if '__' in route_head:
                file_domain = route_head.split('__')[0];
                modulename = f"file_{file_domain}";
            else: 
                file_name, ext = os.path.splitext(route_head);
                if ext == ".md":
                    modulename = 'file_markdown';
                elif ext == ".epub":
                    modulename = 'file_epub';
            return (modulename, url);
        elif scrape_url.startswith("http"):
            split_domain = scrape_url.split('/')[2].split('.');
            if 'www' in split_domain:
                split_domain.remove('www');
            modulename = "_".join(split_domain);
            return (modulename, None);
        elif scrape_url.startswith("meme"):
            return ("meme", None);

        return (None, None);

    def __get_module(self, modulename: str):
        modulename_path = self.__find_module(modulename)
        if modulename_path:
            module = importlib.import_module(modulename_path)
            site = getattr(module, 'SiteScraper') if hasattr(module, 'SiteScraper') else None;
            file = getattr(module, 'FileScraper') if hasattr(module, 'FileScraper') else None;
            storytype = getattr(module, 'get_story_type') if hasattr(module, 'get_story_type') else None;
            return site or file, storytype;
        print('Module not found: %s' % modulename)
        return None, None;

    def __find_module(self, modulename: str):
        if not modulename: return None;
        locations = ['scrape.sites', 'scrape.mangas', 'scrape.files'];
        for location in locations:
            domain_spec = importlib.util.find_spec(f'{location}.{modulename}')
            if domain_spec:
                return f'{location}.{modulename}';