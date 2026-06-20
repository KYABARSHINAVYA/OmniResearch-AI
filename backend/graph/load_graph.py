from graph.relationship_extractor import extract_relationships
from graph.neo4j_store import add_relationship

text = """
Transformers were introduced by Google in 2017.
"""

relationships = extract_relationships(
    text
)

for source, relation, target in relationships:

    add_relationship(
        source,
        relation,
        target
    )

print("Knowledge graph created")
