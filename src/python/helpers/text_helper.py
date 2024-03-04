import json
import re;
import html as htmlParser
from typing import Tuple;
from helpers.scraper_result import ScraperResult
from selectolax.parser import Node, HTMLParser

import importlib
cssutils_spec = importlib.util.find_spec("cssutils")

class TextHelper():
    def setup_chapter(result: ScraperResult, parser = None):
        TextHelper.__set_overflow_visible(result.chapter, parser);
        TextHelper.__change_links(result.chapter);
        TextHelper.__remove_scripts(result.chapter);
        TextHelper.__remove_ads(result.chapter);
        TextHelper.__remove_json(result.chapter);
    
    def __set_overflow_visible(node: Node, parser):
        tds = node.css('div,td');
        for td in tds:
            if 'style' in td.attributes:
                if cssutils_spec:
                    sheet = parser.parseStyle(td.attributes['style']);
                    if sheet.overflow:
                        sheet.overflow = 'visible';
                    if sheet.getProperty('max-width'):
                        print('has max-width', td);
                        sheet.removeProperty('max-width');
                else:
                    td.attrs['style'] = td.attributes['style'].replace('overflow: hidden', 'overflow: visible').replace('overflow: auto', 'overflow: visible').replace('overflow:hidden', 'overflow: visible').replace('overflow:auto', 'overflow: visible');
    
    def __change_links(node: Node):
        links = node.css('a');
        for link in links:
            if 'href' in link.attributes:
                href = link.attributes['href'];
                link.attrs['href'] = 'javascript:void(0)';
                link.attrs['link'] = href;
    
    def __remove_scripts(node: Node):
        scripts = node.css('script');
        for script in scripts:
            script.remove();
    
    def __remove_ads(node: Node):
        scripts = node.css('.adsbygoogle') + node.css('.google-auto-placed') + node.css('.ads');
        for script in scripts:
            script.remove();
    
    def __remove_json(node: Node):
        scripts = node.css('script');
        for script in scripts:
            script.remove();

    def clean_html(result: ScraperResult, parser = None):
        TextHelper.__clean_node(result.chapter, parser);
        result.chapter.unwrap_tags(['element']);
        lines = ScraperResult.get_lines(result.chapter);
        result.lines = lines;

    def __clean_node(node: Node, parser, depth = 0, pad = False, ):
        text = node.text(strip=True);
        if node.tag == 'script':
            node.remove();
        elif node.tag != '-text':
            # remove display style in case of inline tags
            if node.tag == 'img' and node.parent.text(strip=True) == '' and node.parent.tag in TextHelper.__get_inline_tags():
                if 'style' in node.attributes and cssutils_spec:
                    sheet = parser.parseStyle(node.attributes['style']);
                    if sheet.getProperty('display'):
                        # While this does show warnings, it also shows hidden like status tables behind a spoiler tag.
                        sheet.removeProperty('display');
                    node.attrs['style'] = sheet.cssText;

            node = TextHelper.__setups_tables(node);
            padding = node.tag in TextHelper.__get_inline_tags_no_span();

            TextHelper.__merge_inline_twins(node);
            children = TextHelper.__get_children(node);
            
            children = TextHelper.__split_p(node, children);

            # if (node.tag == 'div' and all(x for x in children if x.tag == '-text')):
            #     next_children = [];
            #     for child in children:
            #         cleaned_node = child.html and self.clean_textnode(child);
            #         if not cleaned_node: continue;
            #         cleaned_children = self.get_children(cleaned_node);
            #         if (len(cleaned_children) == 1):
            #             cleaned_child = HTMLParser(f'<p>{cleaned_children[0].html}</p>').body.child;
            #             next_children.append(cleaned_child);
            #         else:
            #             next_children.extend(cleaned_children);
            #     if (len(next_children) > 1):
            #         for next_child in next_children:
            #             node.insert_after(next_child);
            #         node.remove();
            # else:
            for child in children:
                TextHelper.__clean_node(child, parser, depth + 1, padding);
        elif text.strip() != "" and node.parent != None:
            next_node = TextHelper.__clean_textnode(node, pad);
            if next_node:
                node.insert_after(next_node);
            node.remove();
        else:
            node.remove();

    @staticmethod    
    def __get_inline_tags_no_span():
        return ['em', 'strong', 'small', 'b', 'big'];
    @staticmethod
    def __get_inline_tags():
        return ['em', 'strong', 'small', 'b', 'big', 'span'];

    def __get_children(node: Node):
        children: list[Node] = [];
        child = node.child;
        while child:
            children.append(child);
            child = child.next;
        return children;
    
    def __setups_tables(node: Node):
        if node.tag == 'table':
            children = TextHelper.__get_children(node);
            innerHTML = "".join([x.html for x in children]);
            table_replacement = HTMLParser(f'<div class="outer-table"><table>{innerHTML}</table></div>').body.child;
            node.insert_after(table_replacement);
            node.remove();
            return table_replacement.child;
        return node;
    
    def __merge_inline_twins(node: Node):
        children = TextHelper.__get_children(node);
        children_to_merge: list[Tuple[Node, Node]] = [];
        for i in range(len(children) - 1):
            childA = children[i];
            childB = children[i + 1];
            if childA.tag == childB.tag and childA.tag in TextHelper.__get_inline_tags():
                if all(value == childB.attributes[key] for (key, value) in childA.attributes.items()):
                    children_to_merge.append((childA, childB));
        children_to_merge.reverse();
        for (childA, childB) in children_to_merge:
            children_to_move = TextHelper.__get_children(childB);
            for child in children_to_move:
                childA.last_child.insert_after(HTMLParser(f'<element>{child.html}</element>' if child.tag == '-text' else child.html).body.child);
            childB.remove();
        node.unwrap_tags(['element']);
        node.merge_text_nodes();
    
    def __split_p(node: Node, children: list[Node]):
        if (node.tag == 'p'):
            p_containers = [];
            p_container = '';
            for child in children:
                if child.tag == 'br':
                    if not p_container: continue;
                    p_containers.append(p_container);
                    p_container = '';
                else:
                    p_container += child.html;
            if len(p_container.strip()) > 1: p_containers.append(p_container);
            new_children = [];
            p_containers.reverse();
            for p_container in p_containers:
                node.insert_after(HTMLParser(f'<p>{p_container}</p>').body.child);
                for attrKey, attrValue in node.attributes.items():
                    node.next.attrs[attrKey] = attrValue;
                new_children.extend(TextHelper.__get_children(node.next));
            if len(new_children) > 0:
                node.remove();
                return new_children;
        return children;
    
    def __clean_textnode(node: Node, pad = False):
        html = node.html.strip();
        if not html:
            return;
        if html[0] == '{' or html[0] == '[':
            if TextHelper.__is_json(html):
                print(f'Remove tag with json');
                return;
        html = TextHelper.__clean_text(node.html);
        if pad:
            return HTMLParser(f'<element>&nbsp;{html}&nbsp;</element>').body.child;
        else:
            return HTMLParser(f'<element>{html}</element>').body.child;

    @staticmethod
    def __is_json(text: str):
        try:
            json.loads(text)
        except ValueError as e:
            return False
        return True

    @staticmethod
    def __clean_text(html: str):
        html = TextHelper.__remove_disruptive_symbols(html);
        html = TextHelper.__parse_linebreak(html);
        html = TextHelper.__parse_other_whitespaces(html);
        html = TextHelper.__parse_max_5_consecutive_chars(html);
        return html;

    @staticmethod
    def __remove_disruptive_symbols(text: str):
        text = htmlParser.escape(htmlParser.unescape(text));
        return text;

    @staticmethod
    def __parse_linebreak(text: str):
        content = [x.strip() for x in re.split(r'\n', text) if x.strip()];
        return content[0] if len(content) == 1 else ''.join([f'<p>{x}</p>' for x in content]);

    @staticmethod
    def __parse_other_whitespaces(text: str):
        return '&nbsp;'.join([x for x in re.split(r'[\s\u200b\u200c\ufeff]', text) if x.strip()]);

    @staticmethod
    def __parse_max_5_consecutive_chars(text: str):
        return re.sub(r'([^*])\1+', lambda match: match.group()[:5] if len(match.group()) > 5 else match.group(), text);