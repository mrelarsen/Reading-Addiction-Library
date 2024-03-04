from selectolax.parser import HTMLParser, Node
from helpers.story_type import StoryType
from scrape.basic_scraper import BasicScraper;
from scrape.basic_file_scraper import BasicFileScraper;
from scrape.basic_scraper import ScraperResult, KeyResult, UrlResult;
# from epub import open_epub
import zipfile;
from lxml import etree;
import os;

class FileScraper(BasicFileScraper):
    def __init__(self, url: str, driver):
        super().__init__(url);

    def _try_read_file(self, path: str):
        dict = self.epub_info(path);
        htmls = dict['htmls'];
        zip_content = dict['zip_content'];
        bodies = []
        for html in htmls:
            html_path, filename = html;
            parser = HTMLParser(zip_content.read(html_path));
            images = parser.css('img');
            for image in images:
                image.remove();
            body = parser.css_first('body').html;
            bodies.append((filename, body));
        return HTMLParser(f"{''.join(bodies[1])}").body;

    def _scrape(self, body: Node):
        return ScraperResult(
            story_type=StoryType.NOVEL,
            urls = UrlResult(
                prev = None,
                current = f"file:///{self._url}",
                next = None,
            ),
            chapter = body,
            lines = ScraperResult.get_lines(body),
            titles = KeyResult(
                story = None,
                chapter = 'epub',
                domain=None,
            ),
            keys = KeyResult(
                story = None,
                chapter = None,
                domain = None,
            ),
        )

    def epub_info(self, fname: str):
        def xpath(element, path):
            return element.xpath(
                path,
                namespaces={
                    "n": "urn:oasis:names:tc:opendocument:xmlns:container",
                    "pkg": "http://www.idpf.org/2007/opf",
                    "dc": "http://purl.org/dc/elements/1.1/",
                },
            )[0]

        # prepare to read from the .epub file
        zip_content = zipfile.ZipFile(fname)
        
        # find the contents metafile
        cfname = xpath(
            etree.fromstring(zip_content.read("META-INF/container.xml")),
            "n:rootfiles/n:rootfile/@full-path",
        ) 
        
        # grab the metadata block from the contents metafile
        metadata = xpath(
            etree.fromstring(zip_content.read(cfname)), "/pkg:package/pkg:metadata"
        )
        manifest = xpath(
            etree.fromstring(zip_content.read(cfname)), "/pkg:package/pkg:manifest"
        )

        # repackage the data
        dir, _ = os.path.split(cfname);
        htmls = [];
        for tag in manifest:
            _, href_file = os.path.split(tag.get('href'))
            file_name, ext = os.path.splitext(href_file)
            if ext == '.html':
                htmls.append((f"{dir}/{tag.get('href')}", file_name));

        dict = {
            s: xpath(metadata, f"dc:{s}/text()")
            for s in ("title", "language", "date", "identifier")
        } 
        dict['htmls'] = htmls;
        dict['zip_content'] = zip_content;
            
        return dict;