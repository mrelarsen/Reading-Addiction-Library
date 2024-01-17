import sqlite3, uuid
import typing;
from datetime import datetime
from models.reading_status import ReadingStatus
from models.story_type import StoryType
from scrape.basic_scraper import ScraperResult

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if col[0] == 'type':
            d[col[0]] = StoryType(row[idx]).name.lower();
        elif col[0] == 'uuid':
            d[col[0]] = str(uuid.UUID(bytes_le=row[idx]));
        elif col[0] == 'status':
            d[col[0]] = ReadingStatus(row[idx]).name.lower().replace('_', ' ');
        else:
            d[col[0]] = row[idx];
    return d
def dict_factory_pure(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx];
    return d

class StoryDatabase():
    def __init__(self, path = None):
        self.database_path = (path and ((path[:4] == 'file' and path[7:]) or path)) or './database/stories.db';
        conn = sqlite3.connect(self.database_path)
        sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
        sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
        self.__create_db(conn)
        conn.close()

    def __create_db(self, db):
        c = db.cursor();
        content = c.execute("""SELECT name FROM sqlite_master""");
        if len(content.fetchall()) == 0:
            c.execute("""CREATE TABLE story (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid UUID NOT NULL,
                name TEXT NOT NULL,
                desc TEXT NOT NULL,
                type INTEGER,
                rating REAL,
                tags TEXT NOT NULL
                )""")
            c.execute("""CREATE TABLE domain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid UUID NOT NULL,
                key TEXT NOT NULL,
                domain TEXT NOT NULL,
                story_id INTEGER NOT NULL,
                FOREIGN KEY(story_id) REFERENCES story(id)
                )""")
            c.execute("""CREATE TABLE chapter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid UUID NOT NULL,
                name TEXT NOT NULL,
                desc TEXT NOT NULL,
                key TEXT NOT NULL,
                url TEXT NOT NULL,
                status INTEGER,
                created TIMESTAMP,
                updated TIMESTAMP,
                domain_id INTEGER NOT NULL,
                FOREIGN KEY(domain_id) REFERENCES domain(id)
                )""")

    def esc_quotes(self, string):
        new_string = string.replace('"','""');
        return new_string;

    def create_chapter(self, url: str, result: ScraperResult, domain_value: str, status: ReadingStatus):
        print('create chapter', url, domain_value, result.keys.story, result.keys.chapter, result.story_type, result.title);
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure;
        cursor = conn.cursor();
        cursor.execute(f"""SELECT domain.id FROM domain LEFT JOIN story ON story.id = domain.story_id WHERE domain.domain = "{domain_value}" and domain.key = "{result.keys.story}" and story.type = "{result.story_type.value}" """);
        domain = cursor.fetchone();
        domain_id = 0;
        if not domain:
            story_uuid = self.get_unique_identifier(cursor, "story");
            cursor.execute(f"""INSERT INTO story (uuid,name,desc,type,tags) VALUES (?, "", "", "{result.story_type.value}", "")""", (story_uuid,));
            story_id = cursor.lastrowid;
            domain_uuid = self.get_unique_identifier(cursor, "domain");
            cursor.execute(f"""INSERT INTO domain (uuid,key,domain,story_id) VALUES (?, "{result.keys.story}", "{domain_value}", "{story_id}")""", (domain_uuid,));
            domain_id = cursor.lastrowid;
        else: 
            domain_id = domain['id'];
        cursor.execute(f"""SELECT status, id FROM chapter WHERE domain_id = "{domain_id}" and key = "{result.keys.chapter}" """);
        chapter = cursor.fetchone();
        chapter_id = None;
        if not chapter:
            chapter_uuid = self.get_unique_identifier(cursor, "chapter");
            cursor.execute(f"""INSERT INTO chapter (uuid,name,desc,key,url,status,created,domain_id) VALUES (?, "{self.esc_quotes(result.title)}", "", "{result.keys.chapter}", "{self.esc_quotes(url)}", ?, ?, ?)""",
                (chapter_uuid, status.value, datetime.now(), domain_id,));
            chapter_id = cursor.lastrowid;
        else:
            chapter_id = chapter['id']
            status_str = '' if chapter['status'] == ReadingStatus.COMPLETED else ', status = ?';
            cursor.execute(f"""UPDATE chapter SET updated = ? {status_str} WHERE id = {chapter_id} """, (datetime.now(), status.value,))
        conn.commit();
        conn.close();
        return chapter_id;

    def get_stories(self, term = None, pure=False) -> list[dict]:
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure if pure else dict_factory;
        cursor = conn.cursor();
        created_latest_chapter = "(SELECT chapter.created FROM chapter LEFT JOIN domain ON domain.id = chapter.domain_id WHERE story.id = domain.story_id ORDER BY chapter.created DESC LIMIT 1) AS created"
        updated_latest_chapter = "(SELECT chapter.updated FROM chapter LEFT JOIN domain ON domain.id = chapter.domain_id WHERE story.id = domain.story_id and chapter.updated IS NOT NULL ORDER BY chapter.updated ASC LIMIT 1) AS updated"
        key_first_domain = "(SELECT key FROM domain WHERE story.id = domain.story_id LIMIT 1) AS key"
        if pure:
            cursor.execute(f"SELECT * FROM story; ");
        elif not term:
            cursor.execute(f"SELECT *, {created_latest_chapter}, {updated_latest_chapter}, {key_first_domain} FROM story; ");
        else:
            where_match_term = f"""WHERE name LIKE "%{term}%" OR key LIKE "%{term}%" """
            cursor.execute(f"""SELECT *, {created_latest_chapter}, {updated_latest_chapter}, {key_first_domain} FROM story {where_match_term}; """);
        data = cursor.fetchall();
        conn.close();
        return data;

    def get_domains(self, pure=False) -> list[dict]:
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure if pure else dict_factory;
        cursor = conn.cursor();
        cursor.execute("""SELECT * FROM domain """);
        data = cursor.fetchall();
        conn.close();
        return data;

    def get_chapters(self, story_id, pure=False) -> list[dict]:
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure if pure else dict_factory;
        cursor = conn.cursor();
        if not story_id:
            cursor.execute("""SELECT * FROM chapter""");
        else:
            cursor.execute(f"""SELECT chapter.* FROM chapter LEFT JOIN domain ON domain.id = chapter.domain_id WHERE domain.story_id = "{story_id}" """);
        data = cursor.fetchall();
        conn.close();
        return data;

    def get_story(self, story_id, domain_key, domain_domain) -> dict:
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory;
        cursor = conn.cursor();
        if story_id:
            cursor.execute(f"""SELECT * FROM story WHERE id = "{story_id}" """);
        elif domain_key:
            cursor.execute(f"""SELECT story.* FROM domain LEFT JOIN story ON domain.story_id = story.id WHERE domain.key = "{domain_key}" and domain.domain = "{domain_domain}" """);
        data = cursor.fetchall();
        conn.close();
        return data and data[0];

    def get_chapter(self, chapter_id) -> dict:
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory;
        cursor = conn.cursor();
        cursor.execute(f"""SELECT * FROM chapter WHERE id = "{chapter_id}" """);
        data = cursor.fetchall();
        conn.close();
        return data[0];

    def update_chapter(self, chapter_id, chapter_name, chapter_desc, chapter_status:str):
        conn = sqlite3.connect(self.database_path);
        cursor = conn.cursor();
        cursor.execute(f"""UPDATE chapter SET name = "{self.esc_quotes(chapter_name)}", desc = "{self.esc_quotes(chapter_desc)}", status = ? WHERE id = "{chapter_id}" """, (ReadingStatus[chapter_status.upper()].value,));
        conn.commit();
        conn.close();

    def update_story(self, story_id, story_name, story_desc, story_rating, tags):
        conn = sqlite3.connect(self.database_path);
        cursor = conn.cursor();
        cursor.execute(f"""UPDATE story SET name = "{self.esc_quotes(story_name)}", desc = "{self.esc_quotes(story_desc)}", rating = "{story_rating}", tags = "{self.esc_quotes(tags)}" WHERE id = "{story_id}" """);
        conn.commit();
        conn.close();

    def create_chapters_from_entities(self, ext_stories, ext_domains, ext_chapters):
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure;
        cursor = conn.cursor();
        
        existing_stories, ext_stories_map = self.get_existing_by_uuids(cursor, ext_stories, 'story', ['type']);
        existing_domains, ext_domains_map = self.get_existing_by_uuids(cursor, ext_domains, 'domain', ['key', 'domain']);
        existing_chapters, _ = self.get_existing_by_uuids(cursor, ext_chapters, 'chapter', ['key']);
        
        # Get all missing stories, domains and chapters
        missing_story_commands = [];
        missing_domains = [];
        missing_chapters = [];
        # Get all updated stories, domains and chapters
        updated_story_commands = [];
        updated_chapters = [];

        for ext_chapter in ext_chapters:
            existing_chapter = existing_chapters.get(ext_chapter['uuid']);
            if not existing_chapter:
                ext_domain = ext_domains_map[ext_chapter['domain_id']];
                ext_story = ext_stories_map[ext_domain['story_id']];
                existing_domain = existing_domains.get(ext_domain['uuid']) or next((x for x in missing_domains if x[1][0] == ext_domain['uuid']), None);
                if not existing_domain and not next((x for x in missing_domains if x[0] == ext_domain['uuid']), None):
                    existing_story = existing_stories.get(ext_story['uuid']) or next((x for x in missing_story_commands if x[0] == ext_story['uuid']), None);
                    if not existing_story and not next((x for x in missing_story_commands if x[0] == uuid.UUID(bytes_le=ext_story['uuid'])), None):
                        missing_story_commands.append([uuid.UUID(bytes_le=ext_story['uuid']), self.esc_quotes(ext_story['name']), self.esc_quotes(ext_story['desc']), ext_story['type'], ext_story['rating'], ext_story['tags']]);
                    missing_domains.append((ext_story['uuid'], [uuid.UUID(bytes_le=ext_domain['uuid']), ext_domain['key'], ext_domain['domain'], existing_story['id'] if existing_story else 0]));
                missing_chapters.append((ext_domain['uuid'], [uuid.UUID(bytes_le=ext_chapter['uuid']), self.esc_quotes(ext_chapter['name']), self.esc_quotes(ext_chapter['desc']), ext_chapter['key'], self.esc_quotes(ext_chapter['url']), ext_chapter['status'], ext_chapter['created'], ext_chapter['updated'], existing_domain['id'] if existing_domain else 0]));
            else:
                ext_domain = ext_domains_map[ext_chapter['domain_id']];
                ext_story = ext_stories_map[ext_domain['story_id']];
                existing_domain = existing_domains.get(ext_domain['uuid']) or next((x for x in missing_domains if x[1][0] == ext_domain['uuid']), None);
                existing_story = existing_stories.get(ext_story['uuid']) or next((x for x in missing_story_commands if x[0] == ext_story['uuid']), None);
                updated = existing_chapter['updated'] if not ext_chapter['updated'] or (existing_chapter['updated'] and existing_chapter['updated'] > ext_chapter['updated']) else ext_chapter['updated'];
                status = ReadingStatus.COMPLETED if existing_chapter['status'] == ReadingStatus.COMPLETED else ext_chapter['status'];
                if existing_chapter['updated'] != updated or existing_chapter['status'] != status:
                    updated_chapters.append([status, updated, existing_chapter['id']]);
                if next((x for x in updated_story_commands if x['id'] != existing_story['id']), None):
                    rating = existing_story['rating'] if ext_story['rating'] != existing_story['rating'] and (existing_story['rating'] == 0 or existing_story['rating'] == None) else ext_story['rating'];
                    tags = " ".join(self.unique(ext_story['tags'].split(' ') + existing_story['tags'].split(' ')))
                    if existing_story['rating'] != rating or existing_story['tags'] != tags:
                        updated_story_commands.append([rating, tags, existing_story['id']]);
        
        if len(updated_chapters) > 0:
            cursor.executemany("UPDATE chapter SET status=?, updated=? WHERE id=?", updated_chapters);
        if len(updated_story_commands) > 0:
            cursor.executemany("UPDATE story SET rating=?, tags=? WHERE id=?", updated_story_commands);

        
        # Create all missing stories, domains and chapters
        created_stories = [];
        last_story_id = cursor.execute("SELECT max(id) from story").fetchone()['max(id)'];
        cursor.executemany("INSERT INTO story (uuid,name,desc,type,rating,tags) VALUES (?,?,?,?,?,?)", missing_story_commands);
        created_stories = cursor.execute("SELECT id,uuid,name FROM story WHERE id > ? ORDER BY id ASC", (last_story_id,)).fetchall();

        for missing_domain in missing_domains:
            for created_story in created_stories:
                if missing_domain[0] == created_story['uuid']:
                    missing_domain[1][-1] = created_story['id'];
                    break;
        
        last_domain_id = cursor.execute("SELECT max(id) from domain").fetchone()['max(id)'];
        commands = [x[1] for x in missing_domains];
        cursor.executemany("INSERT INTO domain (uuid,key,domain,story_id) VALUES (?,?,?,?)", commands);
        created_domains = cursor.execute(f"SELECT id,uuid,domain,key FROM domain WHERE id > {last_domain_id} ORDER BY id ASC").fetchall();

        for missing_chapter in missing_chapters:
            for created_domain in created_domains:
                if missing_chapter[0] == created_domain['uuid']:
                    missing_chapter[1][-1] = created_domain['id'];
                    break;
        
        last_chapter_id = cursor.execute("SELECT max(id) from chapter").fetchone()['max(id)'];
        commands = [x[1] for x in missing_chapters];
        cursor.executemany("INSERT INTO chapter (uuid,name,desc,key,url,status,created,updated,domain_id) VALUES (?,?,?,?,?,?,?,?,?)", commands);
        created_chapters = cursor.execute(f"SELECT chapter.id,chapter.uuid,chapter.name,chapter.key,domain.id as d_id,domain.domain as d_name,domain.key as d_key,story.id as s_id,story.name as s_name FROM chapter LEFT JOIN domain ON domain.id = chapter.domain_id LEFT JOIN story ON story.id = domain.story_id WHERE chapter.id > {last_chapter_id} ORDER BY chapter.id ASC").fetchall();

        conn.commit();
        conn.close();
        return created_stories, created_domains, created_chapters;

    def unique(self, list1):
        unique_list = [];
        for x in list1:
            if x not in unique_list:
                unique_list.append(x);
        return unique_list;

    def get_unique_identifier(self, cursor: sqlite3.Cursor, type: str):
        for _ in range(0,20):
            next_uuid = uuid.uuid4();
            uuids = cursor.execute(f"SELECT uuid from {type} where uuid = ?", (next_uuid,)).fetchall();
            if (len(uuids) == 0):
                return next_uuid;
        raise Exception("Attempt to get unique identifier failed");

    def get_existing_by_uuids(self, cursor: sqlite3.Cursor, elements, table, keys) -> typing.Tuple[dict, dict]:
        uuids = [x['uuid'] for x in elements];
        sql=f"select * FROM {table} WHERE uuid IN ({','.join(['?']*len(uuids))})";
        existing_stories = cursor.execute(sql, uuids).fetchall();
        return self.existing_has_property(existing_stories, elements, keys, table);

    def existing_has_property(self, exists, elements, properties, table) -> typing.Tuple[dict, dict]:
        exist_dict = {};
        element_dict = {};
        for exist in exists:
            exist_dict[exist['uuid']] = exist;
        for element in elements:
            exist = exist_dict.get(element['uuid']);
            if exist and not all([element[prop] == exist[prop] for prop in properties]):
                print(f"WARNING: {table} with uuid:{uuid.UUID(bytes_le=element['uuid'])} was found with id:{element['id']}, but with a mismatch {[f'{prop}: {exist[prop]} != {element[prop]}' for prop in properties]}, so if was not seen as existing");
                continue;
            element_dict[element['id']] = element;
        return exist_dict, element_dict;

    def merge_stories(self, from_story_ids, to_story_id):
        if not all(from_story_id > to_story_id for from_story_id in from_story_ids):
            print('Warning: not merging due to lowest story_id error');
            return;
        conn = sqlite3.connect(self.database_path);
        conn.row_factory = dict_factory_pure;
        cursor = conn.cursor();
        sql=f"SELECT * FROM story WHERE id IN ({','.join(['?']*(len(from_story_ids)+1))})";
        story_ids = from_story_ids + [to_story_id];
        stories = cursor.execute(sql, story_ids).fetchall();
        to_story = next(story for story in stories if story['id'] == to_story_id);
        from_stories = [story for story in stories if story['id'] in from_story_ids and story['type'] == to_story['type']];
        if len(from_stories) != len(from_story_ids):
            print('Warning: not merging due to type mismatch');
            return;
        # Update to combined descriptions, rating and tags 
        combined_desc = "".join([story['desc'] for story in stories]);
        highest_rating = max([story['rating'] or 0.0 for story in stories]);
        combined_tags = " ".join([story['tags'] for story in stories if story.get('tags')]) or "";
        cursor.execute(f"""UPDATE story SET desc = "{self.esc_quotes(combined_desc)}", rating = "{highest_rating}", tags = "{self.esc_quotes(combined_tags)}" WHERE id = "{to_story_id}" """);
        # Update moved domains
        cursor.execute(f"""UPDATE domain SET story_id = "{to_story_id}" WHERE story_id IN ({','.join(['?']*(len(from_story_ids)))}) """, from_story_ids);
        # Delete moved stories
        cursor.execute(f"""DELETE FROM story WHERE id IN ({','.join(['?']*(len(from_story_ids)))}) """, from_story_ids);
        conn.commit();
        conn.close();
