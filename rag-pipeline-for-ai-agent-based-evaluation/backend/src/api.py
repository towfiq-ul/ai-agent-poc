"""
FastAPI backend for the RAG pipeline.
Exposes REST endpoints consumed by the Django frontend.
"""

import glob
import os
import sys
import tempfile
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Make src/ importable when running from inside src/
sys.path.insert(0, os.path.dirname(__file__))

from impl import Datastore, Evaluator, Indexer, ResponseGenerator, Retriever
from rag_pipeline import RAGPipeline

# ---------------------------------------------------------------------------
# Singleton pipeline — built once on startup, shared across all requests
# ---------------------------------------------------------------------------
_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        datastore = Datastore()
        indexer = Indexer()
        retriever = Retriever(datastore=datastore)
        response_generator = ResponseGenerator()
        evaluator = Evaluator()
        _pipeline = RAGPipeline(datastore, indexer, retriever, response_generator, evaluator)
    return _pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the pipeline (loads embedding model) before accepting traffic."""
    print("🚀 Warming up RAG pipeline …")
    get_pipeline()
    print("✅ Pipeline ready.")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RAG Pipeline API",
    description="Retrieval-Augmented Generation backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]


class IndexResponse(BaseModel):
    indexed: int
    message: str


class EvalRequest(BaseModel):
    questions: List[dict]  # [{question, answer}, ...]


class EvalResult(BaseModel):
    question: str
    response: str
    expected_answer: str
    is_correct: bool
    reasoning: Optional[str] = None


class EvalResponse(BaseModel):
    results: List[EvalResult]
    score: int
    total: int


class StatusResponse(BaseModel):
    status: str
    embedding_model: str
    llm_provider: str
    llm_model: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}


@app.get("/status", response_model=StatusResponse, tags=["System"])
def status():
    return StatusResponse(
        status="ok",
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
        llm_model=os.getenv("AI_AGENT_MODEL", "llama3.2"),
    )


@app.post("/query", response_model=QueryResponse, tags=["RAG"])
def query(req: QueryRequest):
    """Retrieve relevant chunks and generate a grounded answer."""
    pipeline = get_pipeline()
    try:
        chunks, sources = _search_with_sources(pipeline, req.query, req.top_k)
        answer = pipeline.response_generator.generate_response(req.query, chunks)
        return QueryResponse(query=req.query, answer=answer, sources=sources)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/index/files", response_model=IndexResponse, tags=["Index"])
async def index_files(files: List[UploadFile] = File(...)):
    """Upload and index one or more .json, .pdf, .txt or .md files."""
    pipeline = get_pipeline()
    tmp_paths = []
    try:
        for upload in files:
            suffix = os.path.splitext(upload.filename)[1] or ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await upload.read())
                tmp_paths.append(tmp.name)

        items = pipeline.indexer.index(tmp_paths)
        pipeline.datastore.add_items(items)
        return IndexResponse(
            indexed=len(items),
            message=f"Successfully indexed {len(items)} chunks from {len(files)} file(s).",
        )
    except Exception as exc:
        print(f"Exception: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        for p in tmp_paths:
            try:
                os.unlink(p)
            except OSError:
                pass


@app.post("/index/sample", response_model=IndexResponse, tags=["Index"])
def index_sample():
    """Index the built-in sample knowledge base."""
    pipeline = get_pipeline()
    sample_path = os.getenv("SAMPLE_DATA_PATH", "/app/sample_data/source")
    try:
        paths = glob.glob(os.path.join(sample_path, "*"))
        if not paths:
            raise HTTPException(status_code=404, detail=f"No files found at {sample_path}")
        items = pipeline.indexer.index(paths)
        pipeline.datastore.add_items(items)
        return IndexResponse(
            indexed=len(items),
            message=f"Indexed {len(items)} chunks from {len(paths)} sample file(s).",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/reset", tags=["Index"])
def reset():
    """Drop and recreate the vector database table."""
    pipeline = get_pipeline()
    try:
        pipeline.reset()
        return {"message": "Database reset successfully."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/evaluate", response_model=EvalResponse, tags=["Evaluate"])
def evaluate(req: EvalRequest):
    """Run the Q&A evaluation suite using the pipeline's thread pool."""
    pipeline = get_pipeline()
    try:
        eval_results = pipeline.evaluate(req.questions)
        results = [
            EvalResult(
                question=r.question,
                response=r.response,
                expected_answer=r.expected_answer,
                is_correct=r.is_correct,
                reasoning=r.reasoning,
            )
            for r in eval_results
        ]
        score = sum(r.is_correct for r in results)
        return EvalResponse(results=results, score=score, total=len(results))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _search_with_sources(
    pipeline: RAGPipeline, query: str, top_k: int
) -> Tuple[List[str], List[str]]:
    """
    Single embedding call that returns both content chunks and deduplicated
    source filenames. Avoids the double-embedding bug from the original impl.
    """
    vector = pipeline.datastore.get_vector(query)
    rows = (
        pipeline.datastore.table.search(vector)
        .select(["content", "source"])
        .limit(top_k)
        .to_list()
    )

    chunks: List[str] = []
    sources: List[str] = []
    seen_sources: set = set()

    for row in rows:
        content = row.get("content", "")
        src = row.get("source", "")
        # source stored as "filename.md:chunk_index" — strip chunk index
        filename = src.split(":")[0] if ":" in src else src

        if content:
            chunks.append(content)
        if filename and filename not in seen_sources:
            sources.append(filename)
            seen_sources.add(filename)

    return chunks, sources
