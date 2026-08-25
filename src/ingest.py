from pathlib import Path

from src.document_loader import load_pdf
from src.text_splitter import split_documents
from src.vector_store import create_vector_store


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PDF_DIRECTORY = Path("data/pdfs")


# --------------------------------------------------
# Find all PDF files
# --------------------------------------------------

def get_pdf_files():
    pdf_files = sorted(PDF_DIRECTORY.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {PDF_DIRECTORY}"
        )

    return pdf_files


# --------------------------------------------------
# Load all PDFs
# --------------------------------------------------

def load_all_pdfs(pdf_files):

    all_documents = []

    for pdf_file in pdf_files:

        print(f"\nLoading: {pdf_file.name}")

        documents = load_pdf(str(pdf_file))

        # Add filename to metadata
        for document in documents:
            document.metadata["source"] = pdf_file.name

        all_documents.extend(documents)

        print(f"Pages loaded: {len(documents)}")

    return all_documents


# --------------------------------------------------
# Main ingestion pipeline
# --------------------------------------------------

def main():

    print("=" * 60)
    print("COMPANY DOCUMENT AI - DOCUMENT INGESTION")
    print("=" * 60)

    # 1. Find PDFs
    pdf_files = get_pdf_files()

    print(f"\nPDF files found: {len(pdf_files)}")

    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")

    # 2. Load PDFs
    documents = load_all_pdfs(pdf_files)

    print(f"\nTotal pages loaded: {len(documents)}")

    # 3. Split documents
    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    if not chunks:
        raise ValueError("No document chunks were created.")

    # 4. Create Chroma vector store
    print("\nCreating Chroma vector database...")

    create_vector_store(chunks)

    print("\n" + "=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()