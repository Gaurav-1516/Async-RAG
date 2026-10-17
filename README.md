# Async-RAG: Scalable Document-Grounded AI

Async-RAG is a high-performance **Retrieval-Augmented Generation (RAG)** application built with FastAPI and LangChain. It features a decoupled architecture that separates fast document ingestion from long-running AI chat processing using a distributed task queue.

## 🚀 Features

- **Decoupled Architecture**: Web server handles requests while background workers process heavy LLM tasks via Redis Queue (RQ).
- **Synchronous Document Ingestion**: Modern drag-and-drop UI for instant PDF and Text file indexing.
- **Asynchronous Chat**: Scalable chat processing with job status tracking.
- **Vector Search**: Integrated with **Qdrant** for high-speed semantic retrieval.
- **Latest AI Models**: Powered by **Google Gemini 3.7 Flash** and **Gemini Embedding 2**.
- **Context-Grounded Answers**: Engineered prompts ensure answers are strictly based on uploaded documents.

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **LLM Orchestration**: LangChain (LCEL)
- **Task Queue**: Redis + RQ
- **Vector Database**: Qdrant
- **AI Models**: Google Generative AI (Gemini)
- **Template Engine**: Jinja2

## 📋 Prerequisites

- **Python 3.11+** (Highly recommended due to `urllib3` and SSL compatibility on macOS)
- **Redis**: For task queuing
- **Qdrant**: Vector database instance
- **Google Gemini API Key**

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Async-RAG
   ```

2. **Create and activate a Virtual Environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   gemini_key=your_google_gemini_api_key
   ```

## 🏃 How to Run

### 1. Start External Services
If you have Docker installed, use the provided `docker-compose.yml`:
```bash
docker-compose up -d
```
*This starts Redis and Qdrant.*

### 2. Start the RQ Worker
Open a new terminal and run the background worker. 
**Note for macOS users**: You must set the fork safety flag.
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker --with-scheduler
```

### 3. Start the FastAPI Server
In another terminal:
```bash
fastapi dev Async-RAG/main.py
```
Or if using uvicorn directly:
```bash
uvicorn Async-RAG.server:app --reload
```

## 🖥 Usage

1. **Ingest Documents**: Visit `http://localhost:8000/` to upload PDF or TXT files.
2. **Chat**: Use the `/chat` API endpoint to ask questions.
   - **Endpoint**: `POST /chat?query=Your+Question`
   - **Response**: Returns a `job_id`.
3. **Check Status**: Poll the result using the `job_id`.
   - **Endpoint**: `GET /job-status?job_id=<job_id>`

## ⚠️ macOS Note
If you encounter a "Work horse terminated unexpectedly" error during job execution, ensure you are running the worker with:
`OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker`
