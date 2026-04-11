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

from chromadb import ingest

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
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
        loader = TextLoader(str(file_path), encoding="utf-8")
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


def chunk_documents(
    docs: list[Document], chunk_size: int = 512, chunk_overlap: int = 64
) -> list[Document]:
    """
    Split docs into chunks using RecursiveCharacterTextSplitter.
    Preserves source metadata on every chunk.

    Args:
        docs:           Raw LangChain Docs to from load_documents()
        chunk_size:     Max chars per chunk (default: 512)
        chunk_overlap:  Overlap between consecutive chunks (default: 64)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(docs)

    # traceability
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    logger.info(
        f"Split into {len(chunks)} chunks"
        f" (size={chunk_size}, overlap={chunk_overlap})"
    )

    return chunks


def ingest(
    input_path: str | Path, chunk_size: int = 512, chunk_overlap: int = 64
) -> list[Document]:
    """
    Full ingestion pipeline: load -> chunk.
    Returns chunked Docs ready for embedding.

    Args:
        input_path:     Path to file or directory
        chunk_size:     Max chars per chunk
        chunk_overlap:  Overlap between consecutive chunks
    """
    path = Path(input_path)
    docs = load_documents(path)
    chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunks


# ── CLI ───────────────────────────────────────────────────────────────────────
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest documents into chunks.")
    parser.add_argument("--input", required=True, help="Path to file or directory")
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=64)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    chunks = ingest(args.input, chunk_size=args.chunk_size, chunk_overlap=args.overlap)
    print(f"\nDone. {len(chunks)} chunks ready for embedding.")
    print(f"First chunk preview:\n{chunks[0].page_content[:200]!r}")
