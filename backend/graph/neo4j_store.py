
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = None


def get_driver():
    global driver
    if driver is not None:
        return driver

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not username or not password:
        return None

    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver


def add_relationship(
    source,
    relation,
    target
):

    query = """
    MERGE (a:Entity {name:$source})
    MERGE (b:Entity {name:$target})
    MERGE (a)-[:RELATED_TO]->(b)
    """

    active_driver = get_driver()
    if active_driver is None:
        return {"status": "skipped", "reason": "Neo4j is not configured."}

    with active_driver.session() as session:

        session.run(
            query,
            source=source,
            target=target
        )
