
# RAG Chat with ChromaDB, Ollama, and Streamlit

A Retrieval Augmented Generation demo.  
You index PDFs from a `database/` folder into a local ChromaDB store, then query them in a Streamlit chat UI. Embeddings run through Ollama using `nomic-embed-text:v1.5`. The answer model is `qwen3:1.7b`. Responses are summarised in English.

## Features

- PDF ingestion from a folder, automatic chunking.
- Local vector store with ChromaDB PersistentClient.
- Local embeddings via Ollama.
- Simple Streamlit chat with message history and streaming output.
- Quick start on a single machine, no cloud keys.

## How it works

1. **Index step**  
   - Load all PDFs in `database/` with `PyPDFDirectoryLoader`.  
   - Split into overlapping chunks for better retrieval.  
   - Create stable `chunk_id`s per source page and order.  
   - Compute embeddings using Ollama and upsert into a ChromaDB collection.

2. **Query step**  
   - Streamlit chat records messages in `st.session_state`.  
   - Top-k document chunks are fetched from ChromaDB.  
   - The chunks are sent to `qwen3:1.7b` through Ollama with a short prompt.  
   - The response is streamed to the UI.

## Stack

- Python 3.10+
- [ChromaDB] persistent client
- [Ollama] for local models
- [LangChain Community] loaders and text splitters
- Streamlit for the chat UI

## Project structure

```
.
├─ database/                  # put your PDFs here
├─ medical/                   # created at runtime, ChromaDB persistent dir
├─ dbase.py                   # indexer, builds the vector store
├─ query.py                   # Streamlit chat app
└─ README.md
```

## Requirements

- A machine that runs Ollama locally.
- Enough RAM for embeddings and a 1.7B model.
- Python packages listed below.

## Install

```bash
# 1) Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install Python deps
pip install   streamlit   chromadb   langchain-community   langchain-text-splitters   ollama

# 3) Install Ollama (system package from https://ollama.com)
#    Then pull the models used in this repo
ollama pull nomic-embed-text:v1.5
ollama pull qwen3:1.7b
```

## Quick start

1. Put your PDFs in the `database/` folder.
2. Build the vector store.

```bash
python dbase.py
```

This creates a ChromaDB persistent directory named `medical/` and a collection named `aids`.

3. Start the chat UI.

```bash
streamlit run query.py
```

Open the local URL from Streamlit. Ask a question about your PDFs.

## Configuration

| Setting                         | Where                         | Default                         |
|---------------------------------|-------------------------------|---------------------------------|
| PDF folder                      | `dbase.py`                    | `database`                      |
| Chunk size, overlap             | `dbase.py`                    | 1000, 200                       |
| ChromaDB path                   | both files                    | `medical`                       |
| Collection name                 | both files                    | `aids`                          |
| Embedding model                 | both files                    | `nomic-embed-text:v1.5`         |
| Embedding endpoint              | both files                    | `http://localhost:11434`        |
| Answer model                    | `query.py`                    | `qwen3:1.7b`                    |
| Top-k results                   | `query.py`                    | 3                               |

Tip, to start Ollama on a different host or port, set `OLLAMA_HOST`, or change the `url` parameter passed to `OllamaEmbeddingFunction` and the `ollama.generate` call.

## Usage flow

1. Index PDFs once, or re-run when documents change.  
2. Chat, the app retrieves top chunks and streams an answer.  
3. To reset the store, stop the app and delete the `medical/` folder.

## Example prompt

> What antibiotics are discussed in these documents for fish health?

The app will retrieve the most relevant chunks and stream a short, bulleted reply in English.

## Troubleshooting

- **Ollama not reachable**  
  Ensure the Ollama service listens on `http://localhost:11434`. Try `ollama list`. If you run on a remote host, match the `url` in both files.
- **Model not found**  
  Run `ollama pull nomic-embed-text:v1.5` and `ollama pull qwen3:1.7b`.
- **No results**  
  Confirm there are PDFs in `database/`, then re-run `python dbase.py`.
- **High memory use**  
  Reduce `chunk_size`, increase `chunk_overlap` moderately, or use fewer `n_results`.

## Security notes

- Files and embeddings are local. Do not expose your Streamlit app to untrusted networks without hardening.
- PDFs are parsed locally. Validate any third-party PDFs before ingestion.

## Roadmap ideas

- Add sources and page numbers to the chat answer.
- Add reranking before generation.
- Add metadata filters and a simple file manager in the sidebar.
- Switch to async calls for faster streaming.
- Parameterise models and paths with environment variables.

## License

MIT. See `LICENSE`.

**Happy hacking.**
