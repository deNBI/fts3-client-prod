from app.settings import settings

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(levelprefix)s %(asctime)s - %(name)s - %(funcName)s:%(lineno)d]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "internal": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "fts3_client": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "fts3_view": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "models_helper": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "s3_client": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "zenodo": {"handlers": ["default"], "level": settings.LOG_LEVEL}
    },
}
