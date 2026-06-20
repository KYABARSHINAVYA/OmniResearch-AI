import chromadb

client = chromadb.PersistentClient(
    path="./memory_db"
)

collection = client.get_or_create_collection(
    name="chat_memory"
)


def save_memory(question, answer):

    collection.add(
        documents=[
            question + "\n" + answer
        ],
        ids=[
            str(collection.count())
        ]
    )


def retrieve_memory(query):

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    return results["documents"]