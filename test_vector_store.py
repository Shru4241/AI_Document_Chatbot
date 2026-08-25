from src.document_loader import load_pdf
from src.text_splitter import split_documents
from src.vector_store import create_vector_store


pdf_path = "data/pdfs/sample.pdf"

# 1. Load PDF
documents = load_pdf(pdf_path)
print("Pages loaded:", len(documents))

# 2. Split documents
chunks = split_documents(documents)
print("Chunks created:", len(chunks))

# 3. Create vector store
vector_store = create_vector_store(chunks)

print("Vector database created successfully!")