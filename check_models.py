from src.llm import create_llm

client = create_llm()

models = client.models.list()

for model in models.data:
    print(model.id)