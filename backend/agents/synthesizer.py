from config.llm import llm


def synthesize(query, rag_result=None, graph_result=None):

    prompt = f"""
You are an expert AI research assistant.

User Question:
{query}

Document Information:
{rag_result}

Knowledge Graph Information:
{graph_result}

Using all available information:

1. Merge both sources.
2. Remove duplicate information.
3. Explain clearly.
4. Produce a final detailed answer.
"""

    try:
        response = llm.invoke(prompt)

        if hasattr(response, "content"):
            return response.content

        return str(response)

    except Exception as e:
        print("SYNTHESIZER ERROR:", e)

        return f"""
Question:
{query}

Document Result:
{rag_result}

Graph Result:
{graph_result}
"""