from typing import Tuple
import re
import os
import hashlib


def get_format_type(_format: str = "epub") -> int:
    if re.search(r"\bepub\b", _format, re.I):
        format_type = 0
    elif re.search(r"\bmobi\b", _format, re.I):
        format_type = 1
    elif re.search(r"\bpdf\b", _format, re.I):
        format_type = 2
    elif re.search(r"\bhtml\b", _format, re.I):
        format_type = 3
    else:  # default epub format
        format_type = 0

    return format_type


def check_url(url: str, debug: bool = False,
              exit_status: int = 0) -> Tuple[bool, int]:

    if re.search(r"\barchiveofourown.org/series\b", url):
        unsupported_flag = True
    elif re.search(r"\bfanfiction.net/u\b", url):
        unsupported_flag = True
    else:
        unsupported_flag = False

    if unsupported_flag:
        with open("err.log", "a") as file:
            file.write(url)

        exit_status = 1
        return False, exit_status
    else:  # for supported urls
        return True, exit_status

def check_hash(ebook_file: str, cache_hash: str) -> bool:

    with open(ebook_file, 'rb') as file:
        data = file.read()

    ebook_hash = hashlib.md5(data).hexdigest()

    if ebook_hash.strip() == cache_hash.strip():
        hash_flag = True
    else:
        hash_flag = False

    return hash_flag
