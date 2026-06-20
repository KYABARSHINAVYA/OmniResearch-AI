from graph.entity_extractor import extract_entities
from graph.graph_retriever import graph_search
from tools.graph_search import search_graph


def graph_rag_agent(question):

    entities = extract_entities(question)

    context = ""

    for entity, label in entities:

        try:

            results = graph_search(entity)

            if results:
                context += " ".join(results) + " "

        except Exception as e:

            print("Graph search error:", e)

    return context.strip()


def run_graph(query):

    try:

        data = search_graph(query)

        return str(data)

    except Exception as e:

        print("Graph tool error:", e)

        return ""