import os
from typing import List, Any

import lancedb
import pyarrow as pa
from dotenv import load_dotenv
from lancedb.table import Table
from sentence_transformers import SentenceTransformer

from interface.base_datastore import BaseDatastore, DataItem

load_dotenv()

# ---------------------------------------------------------------------------
# Embedding model — loaded once at module level so it is not re-instantiated
# on every Datastore() call. Configured via EMBEDDING_MODEL in .env.
# ---------------------------------------------------------------------------
_embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
print(f"ℹ️  Loading embedding model: {_embedding_model_name}")
_embedding_model = SentenceTransformer(_embedding_model_name)
_VECTOR_DIM: int | None = _embedding_model.get_embedding_dimension()
print(f"ℹ️  Embedding dimensions: {_VECTOR_DIM}")


class Datastore(BaseDatastore):
    DB_TABLE_NAME = "ml-ai-table"

    def __init__(self):
        self.DB_PATH = os.getenv("LANCEDB_PATH", "data/lancedb")
        os.makedirs(self.DB_PATH, exist_ok=True)
        self.vector_db = lancedb.connect(self.DB_PATH)
        self.table: Table = self._get_table()

    def get_vector(self, content: str) -> List[float]:
        """Embed a single string and return it as a plain Python list."""
        return _embedding_model.encode(content, convert_to_numpy=True).tolist()

    def add_items(self, items: List[DataItem]) -> None:
        """Batch-embed and upsert a list of DataItems into LanceDB."""
        if not items:
            print("⚠️  No items to add.")
            return

        print(f"⏳ Embedding {len(items)} chunks …")
        contents = [item.content for item in items]
        sources = [item.source for item in items]

        # Batch encode — much faster than one-by-one for large document sets
        vectors = _embedding_model.encode(
            contents,
            batch_size=64,
            show_progress_bar=True,
            convert_to_numpy=True,
        ).tolist()

        # Build a typed PyArrow Table in one shot to avoid LanceDB's internal
        # incremental buffering that triggers a Rust "Spill" error under load
        arrow_table = pa.table(
            {
                "vector": pa.array(vectors, type=pa.list_(pa.float32(), _VECTOR_DIM)),
                "content": pa.array(contents, type=pa.utf8()),
                "source": pa.array(sources, type=pa.utf8()),
            }
        )

        (
            self.table.merge_insert("source")
            .when_matched_update_all()
            .when_not_matched_insert_all()
            .execute(arrow_table)
        )
        print(f"✅ Upserted {len(items)} items into '{self.DB_TABLE_NAME}'.")

    def search(self, query: str, top_k: int = 5) -> list[Any | None]:
        """Return the top-k most semantically similar content chunks."""
        vector = self.get_vector(query)
        results = (
            self.table.search(vector)
            .select(["content", "source", "_distance"])
            .limit(top_k)
            .to_list()
        )
        return [result.get("content") for result in results]

    def reset(self) -> Table:
        """Drop and recreate the LanceDB table with the correct schema."""
        try:
            self.vector_db.drop_table(self.DB_TABLE_NAME)
        except Exception as exc:
            msg = str(exc).lower()
            if "not found" not in msg and "does not exist" not in msg:
                raise
            print("ℹ️  Table does not exist yet — skipping drop.")

        schema = pa.schema(
            [
                pa.field("vector", pa.list_(pa.float32(), _VECTOR_DIM)),
                pa.field("content", pa.utf8()),
                pa.field("source", pa.utf8()),
            ]
        )
        self.vector_db.create_table(self.DB_TABLE_NAME, schema=schema)
        self.table = self.vector_db.open_table(self.DB_TABLE_NAME)
        print(f"✅ Table reset/created: '{self.DB_TABLE_NAME}' at {self.DB_PATH}")
        return self.table

    def _get_table(self) -> Table:
        """Open the existing table or create a fresh one if it doesn't exist."""
        try:
            return self.vector_db.open_table(self.DB_TABLE_NAME)
        except Exception as exc:
            print(f"ℹ️  Table not found — initialising fresh datastore. ({exc})")
            return self.reset()
