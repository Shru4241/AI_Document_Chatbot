from src.embeddings import create_embeddings
from langchain_chroma import Chroma


embeddings = create_embeddings()

vector_store = Chroma(
    persist_directory="chroma_db",
    collection_name="company_documents",
    embedding_function=embeddings
)

# Get all stored documents
data = vector_store.get(include=["documents"])

documents = data["documents"]

keyword = "D.R.O.P."

matches = [
    document
    for document in documents
    if keyword.lower() in document.lower()
]

print("Keyword matches:", len(matches))

for i, document in enumerate(matches[:3], start=1):
    print(f"\n--- Match {i} ---")
    print(document[:1500])