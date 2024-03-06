from helpers.reading_status import ReadingStatus
from scrape.basic_scraper import ScraperResult
from database.database import StoryDatabase

class History():
    def __init__(self, path: str|None = None):
        self.db = StoryDatabase(path);
        pass

    def add_chapter(self, result: ScraperResult, status=ReadingStatus.COMPLETED):
        return self.db.create_chapter(result, status);

    def get_stories(self, term: str = None):
        return self.db.get_stories(term);

    def get_chapters(self, story_id: int):
        return self.db.get_chapters(story_id);

    def get_story(self, id: int, domain_key:str = None, domain_domain: str = None):
        return self.db.get_story(id, domain_key, domain_domain);

    def get_chapter(self, id: int):
        return self.db.get_chapter(id);

    def save_chapter_details(self, chapter_id: int, chapter_name: str, chapter_desc: str, chapter_status: str):
        return self.db.update_chapter(chapter_id, chapter_name, chapter_desc, chapter_status);
        
    def save_story_details(self, story_id: int, story_name: str, story_desc: str, story_rating: float = 0, tags: str = ''):
        return self.db.update_story(story_id, story_name, story_desc, story_rating, tags);

    def merge_stories(self, from_story_ids: list[int], to_story_id: int):
        self.db.merge_stories(from_story_ids, to_story_id);
    
    def merge_database(self, database_path: str):
        merging_db = StoryDatabase(database_path);
        stories = merging_db.get_stories(pure=True);
        domains = merging_db.get_domains(pure=True);
        unique_domains, domain_id_map = self.__unique_domains(domains);
        chapters = merging_db.get_chapters(story_id=None, pure=True);
        unique_chapters = self.__unique_chapters(chapters, domain_id_map);
        created_stories, created_domains, created_chapters = self.db.create_chapters_from_entities(stories, unique_domains, unique_chapters);
        story_map = {};
        for created_chapter in created_chapters:
            s_id = created_chapter['s_id'];
            d_id = created_chapter['d_id'];
            id = created_chapter['id'];
            if not story_map.get(s_id):
                story_map[s_id] = {'name': created_chapter['s_name']};
            if not story_map[s_id].get(d_id):
                story_map[s_id][d_id] = {'name': created_chapter['d_name'] or created_chapter['d_key']};
            story_map[s_id][d_id][id] = created_chapter;
        for story_id in story_map:
            if story_id == 'name': continue;
            created_story = next((x for x in created_stories if x['id'] == story_id), None);
            if created_story:
                print(f"New story: {created_story['name']}")
            else:
                print(f"Story: {story_map[story_id]['name']}");
            for domain_id in story_map[story_id]:
                if domain_id == 'name': continue;
                created_domain = next((x for x in created_domains if x['id'] == domain_id), None);
                if created_domain:
                    print(f"New domain: {created_domain['domain']}/{created_domain['key']}")
                else:
                    print(f"Domain: {story_map[story_id][domain_id]['name']}");
                for chapter_id in story_map[story_id][domain_id]:
                    if chapter_id == 'name': continue;
                    created_chapter = story_map[story_id][domain_id][chapter_id];
                    print(f"New Chapter: {created_chapter['name']}");
    
    def __unique_domains(self, domain_list: list[dict]):
        unique_list = [];
        map = {};
        for domain in domain_list:
            existing = next((x for x in unique_list if x['key'] == domain['key'] and x['domain'] == domain['domain']), None);
            if not existing: unique_list.append(domain);
            else: map[domain['id']] = existing['id'];
        return unique_list, map;
    
    def __unique_chapters(self, chapter_list: list[dict], domain_id_map: dict[int, int]):
        unique_list = [];
        for chapter in chapter_list:
            if chapter['domain_id'] in domain_id_map: chapter['domain_id'] = domain_id_map[chapter['domain_id']];
            if not next((x for x in unique_list if x['key'] == chapter['key'] and x['domain_id'] == chapter['domain_id']), None):
                unique_list.append(chapter);
        return unique_list;

