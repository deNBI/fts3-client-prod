import logging
from typing import List

from minio import Minio
from minio.deleteobjects import DeleteObject

from app.models.serializers import DatabaseIn, Job, JobFile
from app.s3_client.helpers import get_version_and_path_from_object_name
from app.settings import settings

logger = logging.getLogger("s3_client")


class S3Client:

    @classmethod
    def create_client(cls):
        client = Minio(
            settings.S3_URL,
            access_key=settings.S3_ACCESS_KEY.get_secret_value(),
            secret_key=settings.S3_SECRET_KEY.get_secret_value(),
            secure=True
        )
        return client

    async def filter_database_in(self, db: DatabaseIn):
        client = self.create_client()
        objects = client.list_objects(settings.S3_BUCKET, prefix=db.path, recursive=True)
        delete_list = []
        for obj in objects:
            if obj.is_dir:
                continue
            file_found = False
            version_name, path = get_version_and_path_from_object_name(obj.object_name)
            for version in db.versions:
                if version.name == version_name and version.path == path:
                    if version.path:
                        file_path_prefix = f"{db.path}/{version.name}/{version.path}"
                    else:
                        file_path_prefix = f"{db.path}/{version.name}"
                    for file in version.files:
                        if obj.object_name == f"{file_path_prefix}/{file.get_file_name()}":
                            file_found = True
                            file.skip_transfer = True
                            break
                    break
            if not file_found:
                delete_list.append(DeleteObject(obj.object_name))
        return db, delete_list

    async def remove_objects(self, delete_objects):
        client = self.create_client()
        errors = client.remove_objects(settings.S3_BUCKET, delete_objects)
        for error in errors:
            logger.error(f"Error when deleting object {error}")

    async def abort_multipart_uploads_for_canceled_job(self, job: Job):
        client = self.create_client()
        for file in job.files:
            multiparts = client._list_multipart_uploads( # noqa
                bucket_name=settings.S3_BUCKET,
                prefix=file.file_metadata.filename
            )
            for multipart in multiparts.uploads:
                client._abort_multipart_upload( # noqa
                    bucket_name=settings.S3_BUCKET,
                    object_name=multipart.object_name,
                    upload_id=multipart.upload_id
                )

    async def abort_multipart_uploads_for_canceled_files(self, files: List[JobFile]):
        client = self.create_client()
        for file in files:
            multiparts = client._list_multipart_uploads( # noqa
                bucket_name=settings.S3_BUCKET,
                prefix=file.file_metadata.filename
            )
            for multipart in multiparts.uploads:
                client._abort_multipart_upload( # noqa
                    bucket_name=settings.S3_BUCKET,
                    object_name=multipart.object_name,
                    upload_id=multipart.upload_id
                )
