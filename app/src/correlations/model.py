import logging

from sentence_transformers import SentenceTransformer as ST


class SentenceTransformer:
    _instance = None

    @classmethod
    def load(cls):
        logging.info("Correlation-Analysis|Loading sentence transformer, this will take a while...")
        cls._instance = ST("paraphrase-multilingual-mpnet-base-v2")
        logging.info("Correlation-Analysis|Done loading sentence transformer")

    @classmethod
    def get(cls) -> ST:
        if cls._instance is None:
            cls.load()
        return cls._instance
