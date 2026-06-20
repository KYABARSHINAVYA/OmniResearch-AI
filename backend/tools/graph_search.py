from graph.neo4j_store import driver

def search_graph(query):
    cypher = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    LIMIT 5
    """

    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]