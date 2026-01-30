import os
import pytest
from neo4j import GraphDatabase, Driver

@pytest.fixture(scope="module")
def neo4j_driver() -> Driver:
    """
    Creates a Neo4j driver instance from environment variables and closes it after tests.
    """
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    yield driver
    driver.close()

def test_neo4j_connection(neo4j_driver: Driver):
    """
    Tests if the connection to Neo4j is successful by running a simple query.
    """
    assert neo4j_driver is not None, "Failed to create Neo4j driver."

    try:
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1 AS number")
            record = result.single()
            assert record is not None, "Query returned no result."
            assert record["number"] == 1, "Query returned an unexpected value."
    except Exception as e:
        pytest.fail(f"Neo4j connection test failed with an exception: {e}")

