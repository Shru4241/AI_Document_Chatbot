from langchain_chroma import Chroma

from src.embeddings import create_embeddings


def create_vector_store(chunks):
    embeddings = create_embeddings()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db",
        collection_name="company_documents"
    )

    return vector_store