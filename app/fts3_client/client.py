from typing import List, Dict

import logging
import requests
from app.models.serializers import VersionIn, DatabaseIn, Job
from app.settings import settings
import fts3.rest.client.easy as fts3

logger = logging.getLogger("fts3_client")


class FTS3Client:
    def __init__(self):
        self.fts3_url = settings.FTS3_URL
        self.cert = settings.FTS3_CERT
        self.key = settings.FTS3_KEY
        self.ca = settings.FTS3_CA

    def create_context(self):
        return fts3.Context(self.fts3_url, self.cert, self.key, verify=True, capath=self.ca)

    async def copy_version_to_s3(self, version: VersionIn, database_path: str):
        context = self.create_context()
        transfers = []
        metadata = {
            "database": database_path,
            "version": version.name,
            "path": version.path
        }
        if version.path:
            version_path = f"{version.name}/{version.path}"
        else:
            version_path = version.name
        path = f"{database_path}/{version_path}"
        for file in version.files:
            if file.skip_transfer:
                continue
            file_destination = f"{path}/{file.source.rpartition('/')[2]}"
            file_metadata = {"filename": file_destination}
            transfer = fts3.new_transfer(
                f"{file.source}",
                f"s3s://{settings.S3_URL}/{settings.S3_BUCKET}/"
                f"{file_destination}",
                metadata=file_metadata
            )
            transfers.append(transfer)
        if transfers:
            job = fts3.new_job(
                transfers, s3alternate=True, verify_checksum="none", metadata=metadata
            )
            job_id = fts3.submit(context, job)
            logger.info(f"Job id: {job_id} for {version}.")
            return job_id

    async def filter_database_in_by_active_jobs(self, db_file_in: DatabaseIn) -> (DatabaseIn, Dict, List):
        cancel_dict = {"cancel_jobs": [], "cancel_files": {}}
        check_jobs: List[Job] = []
        unfinished_jobs: List[Job] = await self.get_active_jobs_for_database(db_file_in)
        for job_ in unfinished_jobs:
            job = await self.get_job_status(job_.job_id)
            if job.job_state != "ACTIVE" and job.job_state != "SUBMITTED":
                check_jobs.append(job)
                continue
            version_found = False
            cancel_dict["cancel_files"][job.job_id] = []
            for version in db_file_in.versions:
                if version.name == job.job_metadata.version and version.path == job.job_metadata.path:
                    version_found = True
                    if version.path:
                        path_prefix = f"{db_file_in.path}/{version.name}/{version.path}"
                    else:
                        path_prefix = f"{db_file_in.path}/{version.name}"
                    for job_file in job.files:
                        file_found = False
                        for version_file in version.files:
                            file_path = f"{path_prefix}/{version_file.get_file_name()}"
                            if job_file.file_metadata.filename == file_path \
                                    and job_file.source_surl == version_file.source:
                                file_found = True
                                version_file.skip_transfer = True
                                break
                        if not file_found:
                            cancel_dict["cancel_files"][job.job_id].append(job_file)
                    break
            if not version_found:
                cancel_dict["cancel_jobs"].append(job)
        return db_file_in, cancel_dict, check_jobs

    async def get_job_status(self, job_id):
        context = self.create_context()
        job_status = fts3.get_job_status(context, job_id, list_files=True)
        try:
            job = Job(**job_status)
        except Exception as e:
            logger.exception(e)
            return {}
        logger.info(f"Job status:\n{job}")

        return job

    async def get_all_unfinished_jobs(self):
        params = {
            "time_window": 1,
            "state_in": "ACTIVE,FAILED,FINISHEDDIRTY,CANCELED,SUBMITTED"
        }
        jobs = requests.get(
            f"{self.fts3_url}/jobs",
            params=params,
            cert=(self.cert, self.key),
            verify=self.ca
        )
        jobs = jobs.json()
        # context = self.create_context()
        returned_jobs = []
        # jobs = fts3.list_jobs(context, state_in=['ACTIVE', 'FAILED', 'FINISHEDDIRTY', 'CANCELED', 'SUBMITTED'])
        for job in jobs:
            returned_jobs.append(Job(**job))
        return returned_jobs

    async def get_all_active_jobs(self):
        context = self.create_context()
        returned_jobs = []
        jobs = fts3.list_jobs(context)
        for job in jobs:
            returned_jobs.append(Job(**job))
        return returned_jobs

    async def get_active_jobs_for_database(self, database: DatabaseIn):
        returned_jobs = []
        jobs = await self.get_all_active_jobs()
        for job in jobs:
            if job.job_metadata.database == database.path:
                returned_jobs.append(job)
        return returned_jobs

    async def cancel_job(self, job_id, file_ids=None):
        context = self.create_context()
        cancel_status = fts3.cancel(context=context, job_id=job_id, file_ids=file_ids)
        return cancel_status
