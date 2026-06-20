import wikipedia


def wikipedia_search(query):

    try:
        result = wikipedia.summary(
            query,
            sentences=5
        )

        return result

    except Exception:

        return ""