import logging

from sentence_transformers import SentenceTransformer as ST

from app.config import settings


class SentenceTransformer:
    _instance = None

    @classmethod
    def load(cls):
        logging.info(f"{settings.SERVICE_NAME}|Loading sentence transformer, this will take a while...")
        cls._instance = ST("paraphrase-multilingual-mpnet-base-v2")
        logging.info(f"{settings.SERVICE_NAME}|Done loading sentence transformer")

    @classmethod
    def get(cls) -> ST:
        if cls._instance is None:
            cls.load()
        return cls._instance
