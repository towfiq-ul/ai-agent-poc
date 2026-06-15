# AI RAG Pipeline POC

A modular Retrieval-Augmented Generation (RAG) pipeline built in Python, using **AI Agent** for both embeddings and generation, and **LanceDB** as the vector store.

I built this as a hands-on project alongside my ML/AI studies (HarvardX CS109xa and Google's Gen AI Intensive on Kaggle). The sample knowledge base covers topics I've been learning, transformers, prompt engineering, RAG itself, and ML fundamentals so you can query it and get grounded answers from the course material.

![RAG pipeline diagram](rag-design-basic.png)

## What it does

- **Index documents** — chunk markdown/text files and store embeddings in a vector database
- **Retrieve** — embed a query and find the most semantically similar chunks
- **Generate** — pass retrieved context to Gemini and get a grounded answer
- **Evaluate** — run a Q&A test set and score the pipeline automatically

## Tech stack

| Component        | Tool         |
|------------------|--------------|
| LLM & Embeddings | Any Model    |
| Vector database  | LanceDB      |
| Language         | Python 3.10+ |

No OpenAI key needed. No Cohere key needed.

## Project structure

```
ai-rag-poc/
├── sample_data/
│   ├── source/        # Drop .txt / .md files here to index
│   └── eval/
│       └── sample_questions.json
├── src/
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── create_parser.py
│   ├── impl/          # Concrete implementations
│   ├── interface/     # Abstract base classes
│   └── util/          # Shared helpers
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── rag-design-basic.png
├── README.md
├── requirements.txt
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/towfiq-ul/ai-agent-poc.git
cd ai-agent-poc/ai-rag-poc
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your env values

Get a free key at:
1. [aistudio.google.com](https://aistudio.google.com).
2. [z.ai](https://z.ai)

```bash
cp .env.example .env
```
edit `.env` file and set values in keys below:
```
AI_AGENT_API_KEY=<your_ai_agent_api_key>
AI_AGENT_MODEL=<your_ai_agent_model>
AI_AGENT_ENDPOINT=<your_ai_agent_endpoint>
GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_EMBEDDING_MODEL=<your_gemini_embedding_model>
```

## Usage

All commands are run from the project root.

### Run the full pipeline (index + evaluate)

```bash
python main.py run
```

### Add documents to the index

```bash
python main.py add -p "../sample_data/source/"
```

### Query the pipeline

```bash
python main.py query "What is Chain-of-Thought prompting?"
```

### Evaluate against the test set

```bash
python main.py evaluate -f "../sample_data/eval/sample_questions.json"
```

### Reset the database

```bash
python main.py reset
```

## Sample knowledge base

The `sample_data/source/` folder contains four Markdown files covering:

- `transformers_and_llms.md` — attention mechanism, encoder/decoder models, tokenization, temperature
- `prompt_engineering.md` — zero-shot, few-shot, CoT, ReAct, Tree of Thoughts, Gemini tips
- `rag_and_embeddings.md` — RAG pipeline, vector databases, embeddings, advanced RAG techniques
- `ml_fundamentals.md` — supervised/unsupervised learning, neural networks, evaluation metrics

You can replace these with your own documents to build a RAG pipeline over any knowledge base.

---

**Thank You from [Towfiqul Islam](https://towfiq-ul.github.io)**