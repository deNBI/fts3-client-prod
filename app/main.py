from fastapi import FastAPI
from logging.config import dictConfig
from app.fts3_client.views import router as fts3_router
from app.loggers import log_config
import logging

dictConfig(log_config)
app = FastAPI()
app.include_router(fts3_router)

logger = logging.getLogger("internal")
