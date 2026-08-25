# AI Document Chatbot

An AI-powered document question-answering chatbot that allows users to ask questions about company documents and receive answers using a Retrieval-Augmented Generation (RAG) pipeline.

The project currently uses the **Tata Motors Annual Report 2024-25** as the document source.

## Features

* Upload/process company PDF documents
* Extract text from PDFs
* Split documents into smaller chunks
* Generate vector embeddings
* Store embeddings in ChromaDB
* Retrieve relevant document chunks for a question
* Generate answers using Groq LLM
* Display source document and page numbers
* Handle questions that are not available in the document
* Interactive HTML/CSS/JavaScript chatbot UI
* FastAPI backend
* Query intent and keyword-based retrieval improvements

## Architecture

```text
                    User
                     |
                     v
          HTML / CSS / JavaScript
                     |
                     v
                FastAPI
                     |
                     v
              RAG Pipeline
                     |
          +----------+----------+
          |                     |
          v                     v
    Query Processing       ChromaDB
          |                     |
          |              Relevant Chunks
          |                     |
          +----------+----------+
                     |
                     v
                 Groq LLM
                     |
                     v
              Final Answer
                     |
                     v
              Sources / Pages
```

## RAG Pipeline

The application follows these major steps:

```text
PDF Documents
     |
     v
PDF Loader
     |
     v
Document Chunks
     |
     v
Embedding Model
     |
     v
ChromaDB
     |
     v
User Question
     |
     v
Query Processing
     |
     v
Relevant Document Retrieval
     |
     v
Groq LLM
     |
     v
Answer + Sources
```

## Project Structure

```text
AI_Document_Chatbot/
│
├── data/
│   └── pdfs/
│       └── sample.pdf
│
├── chroma_db/
│
├── src/
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── ingest.py
│   ├── llm.py
│   ├── rag.py
│   ├── text_splitter.py
│   └── vector_store.py
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   └── index.html
│
├── main.py
├── requirements.txt
├── README.md
└── .env
```

## Technologies Used

### Backend

* Python
* FastAPI
* Uvicorn

### RAG / LLM

* LangChain
* Groq
* ChromaDB
* Hugging Face Sentence Transformers

### Document Processing

* PyPDF
* LangChain document loaders
* RecursiveCharacterTextSplitter

### Frontend

* HTML
* CSS
* JavaScript

## Embedding Model

The project uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model converts document chunks and user questions into numerical vector representations.

## Vector Database

The project uses **ChromaDB** to store document embeddings and retrieve relevant document chunks.

The vector database is stored locally in:

```text
chroma_db/
```

## LLM

The application uses the **Groq API** to generate answers from the retrieved document context.

The API key is loaded from the `.env` file.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

Do not commit your `.env` file to GitHub.

## Installation

### 1. Clone the project

```bash
git clone <your-repository-url>
cd AI_Document_Chatbot
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

## Document Ingestion

Place PDF files inside:

```text
data/pdfs/
```

Run the ingestion pipeline:

```powershell
python -m src.ingest
```

The ingestion process:

1. Finds PDF files
2. Loads the PDFs
3. Extracts document pages
4. Splits documents into chunks
5. Generates embeddings
6. Stores the embeddings in ChromaDB

## Run the Application

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

## Testing the RAG Pipeline

The RAG pipeline can also be tested directly from the terminal.

Example:

```powershell
python -c "from src.rag import ask_question; a,s=ask_question('What are Tata Motors net zero targets?'); print('Answer:',a); print('Sources:',s)"
```

Example response:

```text
Net-zero emissions targets:
Passenger Vehicles (PV): 2040
Commercial Vehicles (CV): 2045

Renewable electricity target:
100% renewable electricity use in operations by 2030.
```

## Example Questions

The chatbot can answer questions such as:

### Financial

```text
What was Tata Motors consolidated total revenue from operations for FY2025?
```

```text
What was Tata Motors standalone total revenue from operations for FY2025?
```

### Sustainability

```text
What are Tata Motors net zero targets?
```

```text
What is Tata Motors target for 100% renewable electricity use in operations?
```

```text
What are Tata Motors key sustainability targets?
```

### Company Information

```text
What are the main businesses of Tata Motors?
```

### Acronyms

```text
What does D.R.O.P. stand for?
```

## Source Retrieval

The chatbot returns source information along with the answer.

Example:

```text
Sources:
Page: 198
File: sample.pdf

Page: 82
File: sample.pdf
```

This helps the user verify where the information was retrieved from.

## Handling Missing Information

If the requested information is not available in the document, the system can return:

```text
I could not find this information in the document.
```

This helps reduce unsupported answers when the requested information is outside the document.

## Current Document

The current project has been tested using:

```text
Tata Motors Annual Report 2024-25
```

The PDF is stored under:

```text
data/pdfs/
```

## Important Files

### `main.py`

Creates the FastAPI application and exposes:

```text
/
```

for the chatbot UI and:

```text
/chat
```

for the chat API.

### `document_loader.py`

Loads PDF documents using `PyPDFLoader`.

### `text_splitter.py`

Splits documents into smaller chunks using:

```text
RecursiveCharacterTextSplitter
```

with:

```text
chunk_size = 1000
chunk_overlap = 200
```

### `embeddings.py`

Creates embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### `vector_store.py`

Creates the ChromaDB vector store.

### `ingest.py`

Runs the document ingestion pipeline.

### `rag.py`

Contains the main retrieval and question-answering logic, including query processing, keyword/phrase extraction, retrieval, and answer generation.

### `llm.py`

Creates the Groq API client.

### `index.html`

Contains the chatbot interface.

### `script.js`

Handles frontend interaction and communication with the FastAPI `/chat` endpoint.

### `style.css`

Contains the chatbot UI styling.

## Security

The Groq API key should be stored in `.env`.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

Add `.env` to `.gitignore`:

```text
.env
venv/
__pycache__/
chroma_db/
```

Do not upload API keys or other secrets to GitHub.

## Future Improvements

Possible future improvements include:

* Support for multiple companies/documents
* PDF upload directly from the UI
* Conversation memory
* Better citation display
* Improved retrieval and reranking
* Authentication
* Document management
* Multiple vector database support
* Streaming LLM responses
* Evaluation of RAG accuracy
* Deployment to a cloud platform

## Project Status

**Status: Working Prototype**

The current implementation successfully demonstrates:

* PDF document ingestion
* Text chunking
* Embedding generation
* Vector storage
* Document retrieval
* Query processing
* LLM-based answer generation
* Source/page retrieval
* Interactive chatbot interface
* FastAPI backend
