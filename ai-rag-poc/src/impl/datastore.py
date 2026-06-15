import os
from typing import List

import lancedb
import pyarrow as pa
from dotenv import load_dotenv
from google import genai
from lancedb.table import Table

from interface.base_datastore import BaseDatastore, DataItem

load_dotenv()

_gemini_api_key = os.getenv("GEMINI_API_KEY")
if not _gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in environment")

# google.genai uses a Client object instead of a module-level configure() call.
_genai_client = genai.Client(api_key=_gemini_api_key)

_embedding_model_raw = os.getenv("GEMINI_EMBEDDING_MODEL")
if not _embedding_model_raw:
    raise ValueError("GEMINI_EMBEDDING_MODEL is not set in environment")

# Normalise the prefix exactly once — env var may be "text-embedding-004"
# or the fully-qualified "models/text-embedding-004"; both are accepted.
embedding_model = (
    _embedding_model_raw
    if _embedding_model_raw.startswith("models/")
    else f"models/{_embedding_model_raw}"
)


class Datastore(BaseDatastore):
    DB_TABLE_NAME = "ml-ai-table"

    DB_PATH = os.getenv("LANCEDB_PATH", "data/lancedb")

    def __init__(self):
        # Dimension is detected lazily from the first embedding call so this
        # works with any Gemini embedding model (768, 1536, 3072, etc.).
        self._vector_dimensions: int | None = None
        os.makedirs(self.DB_PATH, exist_ok=True)
        self.vector_db = lancedb.connect(self.DB_PATH)
        self.table: Table = self._get_table()

    @property
    def vector_dimensions(self) -> int:
        if self._vector_dimensions is None:
            probe = self.get_vector("probe")
            self._vector_dimensions = len(probe)
            print(f"ℹ️  Embedding dimensions detected: {self._vector_dimensions}")
        return self._vector_dimensions

    def reset(self) -> Table:
        # BUG FIX: only silently ignore the "table does not exist" case;
        # all other exceptions are re-raised so real errors aren't hidden.
        try:
            self.vector_db.drop_table(self.DB_TABLE_NAME)
        except Exception as exc:
            msg = str(exc).lower()
            if "not found" not in msg and "does not exist" not in msg:
                raise
            print("Table does not exist yet — skipping drop.")

        schema = pa.schema(
            [
                pa.field("vector", pa.list_(pa.float32(), self.vector_dimensions)),
                pa.field("content", pa.utf8()),
                pa.field("source", pa.utf8()),
            ]
        )

        self.vector_db.create_table(self.DB_TABLE_NAME, schema=schema)
        self.table = self.vector_db.open_table(self.DB_TABLE_NAME)
        print(f"✅ Table reset/created: {self.DB_TABLE_NAME} at {self.DB_PATH}")
        return self.table

    def get_vector(self, content: str) -> List[float]:
        # New API: client.models.embed_content() returns EmbedContentResponse.
        # The embedding vector lives at response.embeddings[0].values.
        response = _genai_client.models.embed_content(
            model=embedding_model,
            contents=content,
        )
        return response.embeddings[0].values

    def add_items(self, items: List[DataItem]) -> None:
        if not items:
            print("⚠️  No items to add.")
            return

        # Embed sequentially: the Gemini API is I/O-bound so parallelism
        # yields little benefit, and concurrent futures feeding a list-of-dicts
        # into merge_insert triggers a Rust async "Spill" error inside LanceDB
        # when the result set is large (many chunks across multiple documents).
        entries = [self._convert_item_to_entry(item) for item in items]

        # Convert to a PyArrow Table before calling execute().
        # Passing a pre-built Arrow Table avoids LanceDB's internal incremental
        # Python→Arrow buffering that causes the Spill/IO error under load.
        arrow_table = pa.table(
            {
                "vector": pa.array(
                    [e["vector"] for e in entries],
                    type=pa.list_(pa.float32(), self.vector_dimensions),
                ),
                "content": pa.array([e["content"] for e in entries]),
                "source": pa.array([e["source"] for e in entries]),
            }
        )

        (
            self.table.merge_insert("source")
            .when_matched_update_all()
            .when_not_matched_insert_all()
            .execute(arrow_table)
        )

    def search(self, query: str, top_k: int = 5) -> List[str]:
        vector = self.get_vector(query)
        results = (
            self.table.search(vector)
            .select(["content", "source"])
            .limit(top_k)
            .to_list()
        )
        return [result.get("content") for result in results]

    def _get_table(self) -> Table:
        try:
            return self.vector_db.open_table(self.DB_TABLE_NAME)
        except Exception as exc:
            print(f"Table not found, initialising fresh datastore: {exc}")
            return self.reset()

    def _convert_item_to_entry(self, item: DataItem) -> dict:
        vector = self.get_vector(item.content)
        return {
            "vector": vector,
            "content": item.content,
            "source": item.source,
        }
