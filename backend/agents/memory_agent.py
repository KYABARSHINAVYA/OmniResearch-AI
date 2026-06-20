from memory.semantic_memory import retrieve_memory
from analytics.memory_hits import increment_memory_hits

increment_memory_hits()

def memory_agent(question):

    memories = retrieve_memory(question)

    context = ""

    for memory in memories[0]:

        context += memory + "\n"

    return context