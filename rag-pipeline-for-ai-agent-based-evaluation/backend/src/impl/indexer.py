import os
from typing import List

import fitz

from interface.base_datastore import DataItem
from interface.base_indexer import BaseIndexer

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


class Indexer(BaseIndexer):
    def index(self, document_paths: List[str]) -> List[DataItem]:
        items = []
        for path in document_paths:
            items.extend(self._index_file(path))
        return items

    def _index_file(self, path: str) -> List[DataItem]:
        global text
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            text = self._read_pdf(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        chunks = self._chunk_text(text)
        filename = os.path.basename(path)
        return [DataItem(content=chunk, source=f"{filename}:{i}") for i, chunk in enumerate(chunks)]

    def _read_pdf(self, path: str) -> str:
        doc = fitz.open(path)
        return "\n\n".join(page.get_text() for page in doc)

    def _chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            if end < len(text):
                boundary = text.rfind("\n\n", start, end)
                if boundary != -1 and boundary > start + CHUNK_SIZE // 2:
                    end = boundary
            chunks.append(text[start:end].strip())
            start = end - CHUNK_OVERLAP
        return [c for c in chunks if c]
