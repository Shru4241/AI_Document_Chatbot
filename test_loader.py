from src.document_loader import load_pdf
from src.text_splitter import split_documents
from src.embeddings import create_embeddings

pdf_path = "data/pdfs/sample.pdf"

# Load PDF
documents = load_pdf(pdf_path)

print("Number of pages:", len(documents))

# Split into chunks
chunks = split_documents(documents)

print("Number of chunks:", len(chunks))

# Create embedding model
embeddings = create_embeddings()

# Test embedding
vector = embeddings.embed_query(chunks[0].page_content)

print("Embedding created successfully!")
print("Vector length:", len(vector))
print("First 5 values:", vector[:5])