# Retrieval-Augmented Generation (RAG) and Embeddings

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses by retrieving relevant information from an external knowledge base before generating a response. It addresses the key limitations of LLMs: outdated knowledge, hallucination, and lack of access to private or domain-specific data.

RAG was introduced in the 2020 paper "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" by Lewis et al.

## Why RAG?

- **Fresh data**: LLMs have a training cutoff. RAG allows them to access up-to-date information.
- **Private knowledge**: Index your own documents that the model was never trained on.
- **Reduced hallucination**: The model is grounded in retrieved facts.
- **Transparency**: You can show the sources used to generate a response.
- **Cost-effective**: Cheaper than fine-tuning for knowledge injection.

## RAG Pipeline Components

### 1. Indexing (Offline)
Documents are loaded, split into chunks, converted to embeddings, and stored in a vector database. This happens once (or when documents are updated).

- **Document loading**: PDFs, Markdown files, web pages, etc.
- **Chunking**: Split documents into overlapping or fixed-size chunks. Chunk size affects retrieval quality — too large loses precision, too small loses context.
- **Embedding**: Each chunk is converted to a vector using an embedding model.
- **Storage**: Vectors are stored in a vector database (e.g. LanceDB, Chroma, Pinecone, FAISS).

### 2. Retrieval (Online)
When a user asks a question, it is embedded using the same model, and the closest vectors in the database are retrieved.

- **Similarity search**: Cosine similarity or dot product between query vector and stored vectors.
- **Top-k retrieval**: Return the k most similar chunks.
- **Re-ranking**: A second model re-scores the retrieved chunks for better relevance ordering. Cohere Rerank is a popular option.

### 3. Generation
The retrieved chunks are injected into the prompt as context, and the LLM generates a response grounded in that context.

Typical prompt structure:
```
<context>
{retrieved chunks}
</context>
<question>
{user question}
</question>
Answer the question based only on the context above.
```

## Embeddings

### What are Embeddings?
Embeddings are dense vector representations of text that capture semantic meaning. Similar texts have vectors that are close together in the embedding space. They are produced by encoder models trained on large text corpora.

### Embedding Models
- **OpenAI text-embedding-3-small**: 1536 dimensions, fast and widely used
- **Google text-embedding-004**: 768 dimensions, strong multilingual support, used in this project
- **Sentence Transformers**: Open-source, runs locally
- **Cohere Embed**: Strong multilingual embeddings

### Cosine Similarity
The most common similarity metric for embeddings. Measures the angle between two vectors, ignoring magnitude. A score of 1 means identical direction (very similar), 0 means orthogonal (unrelated), -1 means opposite.

### Embedding Dimensions
Higher dimensions can capture more nuance but increase storage and compute costs. Matryoshka embeddings (e.g. text-embedding-3) allow truncating to fewer dimensions with minimal quality loss.

## Vector Databases

Vector databases are optimized for storing and searching high-dimensional vectors using approximate nearest neighbor (ANN) algorithms.

- **LanceDB**: Lightweight, file-based, great for local and serverless use. Used in this project.
- **Chroma**: Open-source, easy to set up, good for prototyping.
- **Pinecone**: Managed cloud vector database, production-ready.
- **FAISS**: Facebook's library for efficient similarity search, runs in-memory.
- **Weaviate / Qdrant**: Open-source, feature-rich alternatives.

## Advanced RAG Techniques

### Hybrid Search
Combine vector search (semantic) with keyword search (BM25/TF-IDF) for better retrieval coverage. Useful when exact terms matter alongside semantic meaning.

### HyDE (Hypothetical Document Embeddings)
Generate a hypothetical answer to the query, embed that, and use it to search. Often retrieves more relevant chunks than embedding the raw question.

### Contextual Compression
After retrieval, filter or compress the chunks to remove irrelevant parts before passing to the LLM.

### Parent-Child Chunking
Store small chunks for precise retrieval but return their larger parent chunk as context for better coherence.

### Agentic RAG
The LLM decides when and what to retrieve, iterating over multiple retrieval steps to gather enough information before answering.

## Evaluation

RAG pipelines should be evaluated on:
- **Faithfulness**: Is the response grounded in the retrieved context?
- **Answer relevance**: Does the response actually answer the question?
- **Context relevance**: Did the retrieval step return useful chunks?
- **Correctness**: Is the final answer factually right?

Tools like RAGAS provide automated metrics for RAG evaluation.
