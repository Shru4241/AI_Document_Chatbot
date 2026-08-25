import re
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.embeddings import create_embeddings
from src.llm import create_llm


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "what", "which", "who", "whom", "where", "when",
    "why", "how", "does", "do", "did", "has", "have",
    "had", "can", "could", "will", "would", "should",
    "company", "companies", "their", "its", "they",
    "them", "this", "that", "these", "those",
    "and", "or", "but", "for", "from", "with", "about",
    "of", "to", "in", "on", "at", "by", "as", "be",
    "being", "been", "into", "than", "then",
    "tata", "motors"
}


# ============================================================
# CACHED EMBEDDING MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_embeddings():
    return create_embeddings()


# ============================================================
# CACHED VECTOR STORE
# ============================================================

@lru_cache(maxsize=1)
def get_vector_store():

    vector_store = Chroma(
        persist_directory="chroma_db",
        collection_name="company_documents",
        embedding_function=get_embeddings()
    )

    return vector_store


# ============================================================
# CACHED LLM
# ============================================================

@lru_cache(maxsize=1)
def get_llm():
    return create_llm()


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@lru_cache(maxsize=1)
def get_all_documents():

    vector_store = get_vector_store()

    data = vector_store.get(
        include=["documents", "metadatas"]
    )

    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    return list(zip(documents, metadatas))


# ============================================================
# QUERY INTENT
# ============================================================

def detect_query_intent(question):

    q = question.lower()

    intent = {
        "standalone": False,
        "consolidated": False,
        "financial": False,
        "revenue": False,
        "target": False,
        "sustainability": False,
        "acronym": False
    }

    # --------------------------------------------------------
    # Standalone / Consolidated
    # --------------------------------------------------------

    if "standalone" in q:
        intent["standalone"] = True

    if "consolidated" in q:
        intent["consolidated"] = True

    # --------------------------------------------------------
    # Financial intent
    # --------------------------------------------------------

    financial_words = [
        "revenue",
        "profit",
        "income",
        "sales",
        "expense",
        "ebit",
        "ebitda",
        "tax",
        "assets",
        "liabilities",
        "cash flow",
        "financial"
    ]

    if any(word in q for word in financial_words):
        intent["financial"] = True

    if "revenue" in q:
        intent["revenue"] = True

    # --------------------------------------------------------
    # Target / Goal intent
    # --------------------------------------------------------

    target_words = [
        "target",
        "targets",
        "goal",
        "goals",
        "plan",
        "plans",
        "strategy",
        "net-zero",
        "net zero"
    ]

    if any(word in q for word in target_words):
        intent["target"] = True

    # --------------------------------------------------------
    # Sustainability intent
    # --------------------------------------------------------

    sustainability_words = [
        "sustainability",
        "sustainable",
        "climate",
        "decarbonisation",
        "decarbonization",
        "renewable",
        "net zero",
        "net-zero",
        "circular economy",
        "embodied emissions",
        "re100"
    ]

    if any(word in q for word in sustainability_words):
        intent["sustainability"] = True

    # --------------------------------------------------------
    # Acronym intent
    # --------------------------------------------------------

    if re.search(r"(?:[A-Za-z]\.){2,}", question):
        intent["acronym"] = True

    return intent


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(question):

    keywords = []

    # --------------------------------------------------------
    # Acronyms such as:
    # D.R.O.P.
    # E.S.G.
    # --------------------------------------------------------

    acronyms = re.findall(
        r"\b(?:[A-Za-z]\.){2,}[A-Za-z]?\.?",
        question
    )

    for acronym in acronyms:

        clean = acronym.lower().rstrip(".")

        if clean:
            keywords.append(clean)

    # --------------------------------------------------------
    # Normal words
    # --------------------------------------------------------

    words = re.findall(
        r"\b[a-zA-Z0-9][a-zA-Z0-9'-]*\b",
        question.lower()
    )

    for word in words:

        if len(word) <= 2:
            continue

        if word in STOPWORDS:
            continue

        keywords.append(word)

    return list(dict.fromkeys(keywords))


# ============================================================
# PHRASE EXTRACTION
# ============================================================

def extract_phrases(question):

    q = question.lower()

    phrases = []

    important_phrases = [
        "standalone total revenue from operations",
        "consolidated total revenue from operations",
        "total revenue from operations",
        "revenue from operations",
        "revenue from contracts with customers",
        "other operating revenues",

        # Sustainability phrases
        "net zero",
        "net-zero",
        "100% renewable electricity",
        "renewable electricity use in operations",
        "renewable electricity use",
        "renewable electricity",
        "key sustainability targets",
        "sustainability targets",
        "sustainability goals",
        "science based targets",
        "science-based targets",
        "circular economy",
        "embodied emissions",

        # Other project-specific phrases
        "dependency reduction",
        "optimisation programme"
    ]

    for phrase in important_phrases:

        if phrase in q:
            phrases.append(phrase)

    return phrases


# ============================================================
# PAGE RELEVANCE
# ============================================================

def page_relevance(metadata, intent):

    page = metadata.get("page")

    if page is None:
        return 0

    try:
        page = int(page)
    except (ValueError, TypeError):
        return 0

    score = 0

    # --------------------------------------------------------
    # Tata Motors Annual Report structure
    #
    # Consolidated Financials:
    # approximately pages 294 - 418
    #
    # Standalone Financials:
    # approximately pages 419 onwards
    # --------------------------------------------------------

    if intent["standalone"]:

        if page >= 419:
            score += 20
        else:
            score -= 15

    if intent["consolidated"]:

        if 294 <= page <= 418:
            score += 20
        else:
            score -= 15

    return score


# ============================================================
# KEYWORD SEARCH
# ============================================================

def keyword_search(question, top_k=20):

    keywords = extract_keywords(question)
    phrases = extract_phrases(question)
    intent = detect_query_intent(question)

    if not keywords and not phrases:
        return []

    documents = get_all_documents()

    scored_documents = []

    for index, (content, metadata) in enumerate(documents):

        text = content.lower()

        score = 0

        # ----------------------------------------------------
        # Exact phrase matching
        # ----------------------------------------------------

        for phrase in phrases:

            if phrase in text:
                score += 30

        # ----------------------------------------------------
        # Keyword matching
        # ----------------------------------------------------

        for keyword in keywords:

            matches = re.findall(
                rf"\b{re.escape(keyword)}\b",
                text
            )

            score += len(matches)

        # ----------------------------------------------------
        # Page / section relevance
        # ----------------------------------------------------

        score += page_relevance(
            metadata,
            intent
        )

        # ----------------------------------------------------
        # Sustainability-specific boost
        # ----------------------------------------------------

        if intent["sustainability"]:

            sustainability_phrases = [
                "driving net zero",
                "net zero emissions",
                "renewable electricity",
                "100% renewable electricity",
                "science based targets",
                "science-based targets",
                "embodied emissions",
                "circular economy"
            ]

            for phrase in sustainability_phrases:

                if phrase in text:
                    score += 20

        # ----------------------------------------------------
        # Financial-specific boosts
        # ----------------------------------------------------

        if intent["financial"]:

            financial_phrases = [
                "statement of profit and loss",
                "revenue from operations",
                "total revenue from operations",
                "revenue from contracts with customers"
            ]

            for phrase in financial_phrases:

                if phrase in text:
                    score += 8

        # ----------------------------------------------------
        # Standalone financial boost
        # ----------------------------------------------------

        if intent["standalone"]:

            if "standalone financial" in text:
                score += 25

            if "standalone financials" in text:
                score += 25

            if "statement of profit and loss" in text:
                score += 15

        # ----------------------------------------------------
        # Consolidated financial boost
        # ----------------------------------------------------

        if intent["consolidated"]:

            if "consolidated financial" in text:
                score += 25

            if "consolidated financials" in text:
                score += 25

            if "consolidated statement of profit and loss" in text:
                score += 15

        # ----------------------------------------------------
        # Store relevant document
        # ----------------------------------------------------

        if score > 0:

            scored_documents.append(
                (
                    score,
                    index,
                    content,
                    metadata
                )
            )

    # --------------------------------------------------------
    # Highest score first
    # --------------------------------------------------------

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return scored_documents[:top_k]


# ============================================================
# SEMANTIC + KEYWORD COMBINATION
# ============================================================

def combine_results(
    semantic_results,
    keyword_results,
    question,
    top_k=8
):

    intent = detect_query_intent(question)

    combined = {}

    # --------------------------------------------------------
    # Add semantic results
    # --------------------------------------------------------

    for rank, document in enumerate(
        semantic_results,
        start=1
    ):

        key = (
            document.metadata.get("source"),
            document.metadata.get("page"),
            document.page_content[:200]
        )

        if key not in combined:

            combined[key] = {
                "document": document,
                "score": 0
            }

        combined[key]["score"] += 1 / (60 + rank)

    # --------------------------------------------------------
    # Add keyword results
    # --------------------------------------------------------

    for rank, item in enumerate(
        keyword_results,
        start=1
    ):

        keyword_score, _, content, metadata = item

        key = (
            metadata.get("source"),
            metadata.get("page"),
            content[:200]
        )

        if key not in combined:

            document = Document(
                page_content=content,
                metadata=metadata
            )

            combined[key] = {
                "document": document,
                "score": 0
            }

        # Keyword relevance is intentionally stronger
        # than normal RRF semantic ranking.

        combined[key]["score"] += (
            keyword_score * 0.02
        )

        combined[key]["score"] += (
            1 / (60 + rank)
        )

    # --------------------------------------------------------
    # Strong query-specific reranking
    # --------------------------------------------------------

    for item in combined.values():

        document = item["document"]

        text = document.page_content.lower()

        metadata = document.metadata

        # ----------------------------------------------------
        # Section relevance
        # ----------------------------------------------------

        item["score"] += page_relevance(
            metadata,
            intent
        ) * 0.05

        # ----------------------------------------------------
        # Sustainability reranking
        # ----------------------------------------------------

        if intent["sustainability"]:

            sustainability_phrases = [
                "driving net zero",
                "net zero emissions",
                "renewable electricity",
                "100% renewable electricity",
                "science based targets",
                "science-based targets",
                "embodied emissions",
                "circular economy",
                "specific commitments, goals and targets"
            ]

            for phrase in sustainability_phrases:

                if phrase in text:
                    item["score"] += 4

            # Strong preference for pages containing
            # Tata Motors sustainability targets.

            target_phrases = [
                "committed to achieving",
                "committed to setting",
                "committed to achieving 100%",
                "internal targets",
                "specific commitments, goals and targets"
            ]

            for phrase in target_phrases:

                if phrase in text:
                    item["score"] += 5

        # ----------------------------------------------------
        # Exact financial phrases
        # ----------------------------------------------------

        if intent["revenue"]:

            if "total revenue from operations" in text:
                item["score"] += 3

            if "revenue from operations" in text:
                item["score"] += 1

        # ----------------------------------------------------
        # Standalone
        # ----------------------------------------------------

        if intent["standalone"]:

            if "standalone financial" in text:
                item["score"] += 5

            if "standalone financials" in text:
                item["score"] += 5

            if "statement of profit and loss" in text:
                item["score"] += 3

            # Strong preference for standalone pages

            page = metadata.get("page")

            try:
                page = int(page)
            except (ValueError, TypeError):
                page = -1

            if page >= 419:
                item["score"] += 2

        # ----------------------------------------------------
        # Consolidated
        # ----------------------------------------------------

        if intent["consolidated"]:

            if "consolidated financial" in text:
                item["score"] += 5

            if "consolidated financials" in text:
                item["score"] += 5

            if "consolidated statement of profit and loss" in text:
                item["score"] += 3

            page = metadata.get("page")

            try:
                page = int(page)
            except (ValueError, TypeError):
                page = -1

            if 294 <= page <= 418:
                item["score"] += 2

    # --------------------------------------------------------
    # Final ranking
    # --------------------------------------------------------

    ranked = sorted(
        combined.values(),
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        item["document"]
        for item in ranked[:top_k]
    ]


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        source = result.metadata.get(
            "source",
            "Company Document"
        )

        page = result.metadata.get(
            "page"
        )

        context_parts.append(
            f"""
Document Section {index}
Source: {source}
Page: {page}

Content:
{result.page_content}
"""
        )

    return "\n\n".join(context_parts)


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(question, context):

    return f"""
You are a professional Company Document Intelligence Assistant.

Answer the user's question using ONLY the information contained
in the document context.

IMPORTANT RULES:

1. Do not invent facts, numbers, dates, targets, or plans.

2. Use ONLY information supported by the document context.

3. Always identify the exact financial figure requested.

4. Financial terms are NOT automatically interchangeable.

For example, carefully distinguish between:

- Revenue
- Revenue from operations
- Total revenue from operations
- Revenue from contracts with customers
- Other operating revenues
- Total income
- Profit
- Profit before tax
- Profit after tax

5. If the user asks for STANDALONE information, use the
   Standalone Financials section and do NOT answer using
   Consolidated Financials.

6. If the user asks for CONSOLIDATED information, use the
   Consolidated Financials section and do NOT answer using
   Standalone Financials.

7. If multiple figures exist, explain the difference clearly.

8. Always include FY / financial year when available.

9. Never calculate or combine financial figures unless the
   document itself supports that calculation.

10. For future plans, targets, goals, sustainability,
    climate commitments, Net Zero goals, renewable energy
    commitments, and strategy, use only information explicitly
    supported by the document.

11. If the requested information is not present in the context,
    answer exactly:

    I could not find this information in the document.

12. Keep the answer concise and directly related to the question.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(question):

    question = question.strip()

    if not question:

        return (
            "Please enter a question.",
            []
        )

    # ========================================================
    # 1. Detect query
    # ========================================================

    intent = detect_query_intent(question)

    # ========================================================
    # 2. Semantic search
    #
    # Retrieve more candidates than before.
    # This gives the reranker more information to work with.
    # ========================================================

    vector_store = get_vector_store()

    semantic_results = vector_store.similarity_search(
        question,
        k=20
    )

    # ========================================================
    # 3. Keyword search
    # ========================================================

    keyword_results = keyword_search(
        question,
        top_k=20
    )

    # ========================================================
    # 4. Combine + rerank
    # ========================================================

    results = combine_results(
        semantic_results,
        keyword_results,
        question,
        top_k=8
    )

    # ========================================================
    # 5. No results
    # ========================================================

    if not results:

        return (
            "I could not find this information in the document.",
            []
        )

    # ========================================================
    # 6. Build context
    # ========================================================

    context = build_context(results)

    # ========================================================
    # 7. Build prompt
    # ========================================================

    prompt = build_prompt(
        question,
        context
    )

    # ========================================================
    # 8. Generate answer
    # ========================================================

    client = get_llm()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        reasoning_effort="low",
        max_tokens=350,
        include_reasoning=False
    )

    answer = response.choices[0].message.content

    # ========================================================
    # 9. Collect sources
    # ========================================================

    sources = []

    for result in results:

        metadata = result.metadata

        source = {
            "page": metadata.get("page"),
            "source": metadata.get(
                "source",
                "Company Document"
            )
        }

        if source not in sources:

            sources.append(source)

    # ========================================================
    # 10. Return
    # ========================================================

    return answer, sources
