from typing import List, Any, Dict
from pydantic import BaseModel


class FileIn(BaseModel):
    source: str
    hash: str | None = None
    directory: bool = False
    zenodo: bool | None = False
    skip_transfer: bool = False
    allow_filter: List[str] = []
    ignore_filter: List[str] = []

    def get_file_name(self):
        return self.source.rpartition('/')[2]


class VersionIn(BaseModel):
    name: str
    path: str | None = None
    files: List[FileIn] = []


class DatabaseIn(BaseModel):
    name: str
    path: str | None = None
    versions: List[VersionIn] = []

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.path is None:
            self.path = self.name


class JobFileMetadata(BaseModel):
    filename: str


class JobFile(BaseModel):
    file_id: int
    file_state: str
    source_surl: str
    file_metadata: JobFileMetadata


class JobMetadata(BaseModel):
    database: str
    version: str
    path: str | None = None


class Job(BaseModel):
    job_state: str
    job_id: str
    job_metadata: JobMetadata
    files: List[JobFile] = []
