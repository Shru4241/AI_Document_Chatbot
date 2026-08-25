# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.rag import ask_question, get_embeddings


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Company Document AI Assistant",
    description="AI-powered chatbot for asking questions from company documents",
    version="1.0.0"
)


# --------------------------------------------------
# Load AI model when server starts
# --------------------------------------------------

@app.on_event("startup")
async def startup_event():

    print("Loading embedding model...")

    get_embeddings()

    print("Embedding model loaded successfully.")


# --------------------------------------------------
# Static Files
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# --------------------------------------------------
# HTML Templates
# --------------------------------------------------

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# --------------------------------------------------
# Chat API
# --------------------------------------------------

@app.post("/chat")
async def chat(data: dict):

    question = data.get("question", "").strip()

    # Check if question is empty
    if not question:

        return JSONResponse(
            content={
                "answer": "Please enter a question.",
                "sources": []
            }
        )

    try:

        # Ask question to RAG pipeline
        answer, sources = ask_question(question)

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "answer": f"Error: {str(e)}",
                "sources": []
            }
        )
