"""
pipeline/ingest.py
Load documents from disk, chunk them, and return a list of LangChain Docs.
Supports .pdfs & .txt files.

Usage:
  python -m pipeline.ingest --input ./docs/
  python -m pipeline.ingest --input ./docs/file.pdf --chunk-size 500 --overlap 50
"""

import argparse
import logging
from pathlib import Path

from langchain.core.document import Document
from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def load_document(file_path: Path) -> list[Document]:
    """
    Load a single .pdf/.txt file and return raw LangChain Docs.
    """

    ext = file_path.suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(str(file_path))
    elif ext == ".txt":
        loader = PyPDFLoader(str(file_path), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    docs = loader.load()
    logger.info(f"Loaded {len(docs)} pages(s) from {file_path.name}")
    return docs


def load_documents(input_path: Path) -> list[Document]:
    """
    Load all supported documents from a directory or single file.

    Returns:
        A flat list of LangChain Docs w/ source metadata.
    """
    docs = []

    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")
        docs.extend(load_document(input_path))

    elif input_path.is_dir():
        files = [
            f
            for f in sorted(input_path.rglob("*"))
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        if not files:
            raise ValueError(f"No supported fiels found in {input_path}")

        for file in files:
            try:
                docs.extend(load_document(file))
            except Exception as e:
                logging.warning(f"Skipping {file.name}: {e}")
    else:
        raise FileNotFoundError(f"Path no found: {input_path}")

    logger.info(f"Total pages/sections loaded: {len(docs)}")
    return docs
