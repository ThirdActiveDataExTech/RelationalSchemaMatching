import logging

import torch
from sentence_transformers import SentenceTransformer as ST

from app.config import settings


class SentenceTransformer:
    """Singleton wrapper for SentenceTransformer model."""
    _instance = None

    @classmethod
    def _load(cls):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"{settings.SERVICE_NAME}|Loading sentence transformer to {device}, this will take a while...")

        if device == "cuda":
            cls._instance = ST("paraphrase-multilingual-mpnet-base-v2").to(torch.device(device))
        else:
            cls._instance = ST("paraphrase-multilingual-mpnet-base-v2")

        logging.info(f"{settings.SERVICE_NAME}|Done loading sentence transformer on {device}")

    @classmethod
    def get(cls) -> ST:
        """Get the SentenceTransformer instance.

        Returns:
            ST: The SentenceTransformer instance.
        """
        if cls._instance is None:
            cls._load()
            assert cls._instance is not None
        return cls._instance
