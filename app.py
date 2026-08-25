import streamlit as st
from src.rag import ask_question


# Page configuration
st.set_page_config(
    page_title="Tata Motors AI Document Chatbot",
    page_icon="🤖",
    layout="centered"
)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Title
st.title("🤖 Tata Motors AI Document Chatbot")

st.write(
    "Ask questions about the Tata Motors Annual Report 2024-25."
)

st.divider()


# Display previous conversation
for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.write(message["content"])

    else:

        with st.chat_message("assistant"):
            st.write(message["content"])

            # Show sources if available
            if message.get("sources"):

                with st.expander("📚 View Sources"):

                    for source in message["sources"]:

                        st.write(
                            f"📄 Page: {source['page']} | "
                            f"File: {source['source']}"
                        )


# Chat input
question = st.chat_input(
    "Ask a question about the Tata Motors report..."
)


# Process question
if question:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # Display user message
    with st.chat_message("user"):
        st.write(question)


    # Prepare conversation context
    previous_questions = []

    for message in st.session_state.messages[:-1]:

        if message["role"] == "user":
            previous_questions.append(message["content"])


    conversation_context = ""

    if previous_questions:

        conversation_context = (
            "\nPrevious questions in this conversation:\n"
            + "\n".join(previous_questions[-3:])
            + "\n\n"
        )


    # Create query for RAG
    rag_question = (
        conversation_context
        + "Current question:\n"
        + question
    )


    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner(
            "Searching the document and generating answer..."
        ):

            answer, sources = ask_question(rag_question)


        st.write(answer)


        # Display sources
        if sources:

            with st.expander("📚 View Sources"):

                for source in sources:

                    st.write(
                        f"📄 Page: {source['page']} | "
                        f"File: {source['source']}"
                    )


    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )


# Sidebar
with st.sidebar:

    st.header("📖 About")

    st.write(
        "This chatbot uses RAG to answer questions "
        "from the Tata Motors Annual Report 2024-25."
    )

    st.write("### Technologies")

    st.write(
        """
        - Python
        - Streamlit
        - LangChain
        - ChromaDB
        - Hugging Face Embeddings
        - Groq LLM
        """
    )


    # Clear conversation
    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


st.divider()

st.caption(
    "Powered by ChromaDB + Hugging Face Embeddings + Groq"
)