
from graph.neo4j_store import get_driver

def graph_search(entity):

    query = """
    MATCH (a:Entity {name:$entity})-[r]->(b)
    RETURN b.name
    """

    driver = get_driver()
    if driver is None:
        return []

    with driver.session() as session:

        result = session.run(
            query,
            entity=entity
        )

def graph_search(entity):
    try:
        driver = get_driver()
        if driver is None:
            return []
        with driver.session() as session:
            result = session.run(
                """
                MATCH (a:Entity {name:$entity})-[r]->(b)
                RETURN b.name
                """,
                entity=entity
            )
            return [record["b.name"] for record in result]

    except Exception as e:
        print("Neo4j error:", e)
        return []

        data = []

        for record in result:

            data.append(
                record["b.name"]
            )

        return data
        
