import json
from typing import List

from app.models.serializers import FileIn
from app.transformers import http
import logging

ZENODO_DOI_PREFIX: str = "10.5281/zenodo."
ZENODO_RECORDS_API: str = "https://zenodo.org/api/records/"

logger = logging.getLogger("zenodo")


def get_record_by_doi(zenodo_doi: str):
    if not zenodo_doi.startswith(ZENODO_DOI_PREFIX):
        return None
    try:
        resp = http.request("GET", f"{ZENODO_RECORDS_API}{zenodo_doi.split(ZENODO_DOI_PREFIX)[1]}")
        resp = json.loads(resp.data.decode("utf-8"))
        return resp
    except Exception as e:
        logger.exception(e)
        return None


async def get_files_by_doi(zenodo_doi: str):
    record = get_record_by_doi(zenodo_doi)

    if record is None:
        return []

    file_array = record["files"]
    returned_files: List[FileIn] = []

    for file in file_array:
        file_in: FileIn = FileIn(source=file["links"]["self"])
        returned_files.append(file_in)

    return returned_files
