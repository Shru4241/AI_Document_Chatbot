from src.rag import ask_question


question = "What are Tata Motors' net-zero emission targets?"

answer, sources = ask_question(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)

print("\nSources:")

for source in sources:
    print(
        f"Page: {source['page']} | "
        f"File: {source['source']}"
    )