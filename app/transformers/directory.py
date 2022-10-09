from typing import List
import re
from bs4 import BeautifulSoup
from app.models.serializers import FileIn
from app.transformers import http


async def directory_file_to_files_list(file: FileIn) -> List[FileIn]:
    if not file.directory:
        return []
    file.skip_transfer = True
    files: List[FileIn] = []
    resp = http.request("GET", file.source)
    soup = BeautifulSoup(resp.data, "html.parser")
    a_elements = soup.findAll("a")
    for a_element in a_elements:
        link = a_element.get("href")
        if link[-1] == "/":
            continue
        elif link.find("index.html") != -1:
            continue
        elif not file_allowed(link, file.allow_filter):
            continue
        elif file_ignored(link, file.ignore_filter):
            continue
        else:
            if not link.startswith("http"):
                if file.source[-1] == "/":
                    source = f"{file.source}{link}"
                else:
                    source = f"{file.source}/{link}"
            else:
                source = link
            new_file = FileIn(source=source)
            files.append(new_file)
    return files


def file_allowed(link: str, allow_filters):
    if not allow_filters:
        return True
    for allow_filter in allow_filters:
        if re.search(allow_filter, link):
            return True
    return False


def file_ignored(link: str, ignore_filters):
    if not ignore_filters:
        return False
    for ignore_filter in ignore_filters:
        if re.search(ignore_filter, link):
            return True
    return False
