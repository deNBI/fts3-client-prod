from typing import List

from app.models.serializers import Job


async def jobs_to_minio_exclude_string(jobs: List[Job]):
    exclude_string = ""
    for job in jobs:
        if job.job_metadata.path:
            exclude_string += f"--exclude \"/{job.job_metadata.database}/{job.job_metadata.version}/{job.job_metadata.path}/*\" "
        else:
            exclude_string += f"--exclude \"/{job.job_metadata.database}/{job.job_metadata.version}/*\" "
    return exclude_string
