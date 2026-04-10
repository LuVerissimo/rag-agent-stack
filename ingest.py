"""
pipeline/ingest.py
Load documents from disk, chunk them, and return a list of LangChain Docs.
Supports .pdfs and .txt files.

Usage:
  python -m pipeline.ingest --input ./docs/
  python -m pipeline.ingest --input ./docs/file.pdf --chunk-size 500 --overlap 50
"""
