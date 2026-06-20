
def extract_relationships(text):

    relationships = []

    words = text.split()

    for i in range(len(words)-1):

        relationships.append(
            (
                words[i],
                "RELATED_TO",
                words[i+1]
            )
        )

    return relationships
