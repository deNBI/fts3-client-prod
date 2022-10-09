from typing import List

from fastapi import APIRouter, Depends
from fastapi.openapi.models import APIKey
import logging
from app.dependencies.key_auth import get_api_key
from app.dependencies.fts3_client import fts3_client
from app.dependencies.s3_client import s3_client
from app.models.serializers import DatabaseIn, Job, FileIn
from app.transformers.directory import directory_file_to_files_list
from app.transformers.zenodo import get_files_by_doi

router = APIRouter()
logger = logging.getLogger("fts3_view")


@router.post("/transfer")
async def add_copy_jobs_from_database_file(
        db_file_in: DatabaseIn,
        api_key: APIKey = Depends(get_api_key)):
    for version in db_file_in.versions: # noqa
        for file in version.files:
            if file.directory:
                files_additional: List[FileIn] = await directory_file_to_files_list(file)
                version.files.extend(files_additional)
            elif file.zenodo:
                file.skip_transfer = True
                files_additional: List[FileIn] = await get_files_by_doi(file.source)
                version.files.extend(files_additional)
    db_file_in, cancel_dict, check_jobs = await fts3_client.filter_database_in_by_unfinished_jobs(db_file_in)
    for job in cancel_dict["cancel_jobs"]:
        logger.info(f"Cancelling {job}.")
        await fts3_client.cancel_job(job_id=job.job_id)
        logger.info(f"Aborting multipart upload for {job}.")
        await s3_client.abort_multipart_uploads_for_canceled_job(job)
    for job_id, files in cancel_dict["cancel_files"].items():
        if not files:
            continue
        logger.info(f"Cancelling {files} for {job_id}.")
        file_ids = [file.file_id for file in files]
        await fts3_client.cancel_job(job_id=job_id, file_ids=file_ids)
        logger.info(f"Aborting multipart upload for {files}.")
        await s3_client.abort_multipart_uploads_for_canceled_files(files)
    started_jobs = {}
    db_file_in, delete_list = await s3_client.filter_database_in(db_file_in)
    await s3_client.remove_objects(delete_list)
    for version in db_file_in.versions:
        version.files = [file for file in version.files if not file.skip_transfer]
    db_file_in.versions = [version for version in db_file_in.versions if version.files]
    for version in db_file_in.versions:
        job_id = await fts3_client.copy_version_to_s3(
            version=version,
            database_path=db_file_in.path
        )
        if version.path:
            version_key = f"{version.name}/{version.path}"
        else:
            version_key = version.name
        started_jobs[version_key] = job_id

    return started_jobs


@router.post("/transfer/dry")
async def dry_add_copy_jobs_from_database_file(
        db_file_in: DatabaseIn,
        api_key: APIKey = Depends(get_api_key)):
    for version in db_file_in.versions: # noqa
        for file in version.files:
            if file.directory:
                files_additional: List[FileIn] = await directory_file_to_files_list(file)
                version.files.extend(files_additional)
            elif file.zenodo:
                file.skip_transfer = True
                files_additional: List[FileIn] = await get_files_by_doi(file.source)
                version.files.extend(files_additional)
    db_file_in, cancel_dict, check_jobs = await fts3_client.filter_database_in_by_unfinished_jobs(db_file_in)
    db_file_in, delete_list = await s3_client.filter_database_in(db_file_in)
    for version in db_file_in.versions:
        version.files = [file for file in version.files if not file.skip_transfer]
    db_file_in.versions = [version for version in db_file_in.versions if version.files]
    returned_dict = {
        "to_cancel_and_abort": cancel_dict,
        "to_delete": delete_list,
        "to_transfer": db_file_in,
        "faulty_job_status": check_jobs
    }
    return returned_dict


@router.get("/transfer/{job_id}", response_model=Job)
async def get_job_status(
        job_id: str,
        api_key: APIKey = Depends(get_api_key)):
    return await fts3_client.get_job_status(job_id)


@router.delete("/transfer/{job_id}")
async def cancel_job(
        job_id: str,
        api_key: APIKey = Depends(get_api_key)):
    return await fts3_client.cancel_job(job_id)


@router.get("/transfers")
async def get_all_jobs_status(api_key: APIKey = Depends(get_api_key)):
    return await fts3_client.get_all_unfinished_jobs()
