from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3"
)

response = llm.invoke("Who are you?")

print(response.content)