# AI Document Chatbot

An AI-powered document question-answering chatbot built using **Retrieval-Augmented Generation (RAG)**. The application allows users to ask questions about company documents and receive AI-generated answers based on the retrieved document content, along with source pages.

The project has been tested using the **Tata Motors Annual Report 2024-25**.

## 🚀 Features

- 📄 PDF document processing
- ✂️ Intelligent text chunking
- 🔢 Vector embedding generation
- 🗄️ ChromaDB vector database
- 🔍 Semantic document retrieval
- 🤖 Groq LLM-based answer generation
- 📚 Source document and page retrieval
- 🛡️ Handles information not available in the document
- 🧠 Query intent and keyword-based retrieval improvements
- 💬 Interactive HTML/CSS/JavaScript chatbot
- ⚡ FastAPI backend
- 🧪 RAG pipeline testing scripts

## 🏗️ Architecture

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
             +------------+------------+
             |                         |
             v                         v
      Query Processing             ChromaDB
             |                         |
             |                  Relevant Chunks
             |                         |
             +------------+------------+
                          |
                          v
                       Groq LLM
                          |
                          v
                    Final Answer
                          |
                          v
                   Sources / Pages