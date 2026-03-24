"""Neo4jデータベース接続テスト"""

import os
from collections.abc import Generator

import pytest
from neo4j import Driver, GraphDatabase

from lakda.db import Neo4jGraphStoreManager


@pytest.fixture(scope="module")
def neo4j_driver() -> Generator[Driver]:
    """環境変数からNeo4jドライバーインスタンスを生成し、テスト後にクローズする"""
    uri = os.getenv("DATABASE_URL_BOLT", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    yield driver
    driver.close()


@pytest.mark.db
class TestNeo4jConnection:
    """Neo4jデータベース接続確認テスト"""

    def test_driver_created(self, neo4j_driver: Driver):
        """ドライバーインスタンスが正常に生成されること"""
        assert neo4j_driver is not None

    def test_connectivity(self, neo4j_driver: Driver):
        """Neo4jサーバーへの接続が成功すること"""
        neo4j_driver.verify_connectivity()

    def test_simple_query(self, neo4j_driver: Driver):
        """簡単なCypherクエリが実行できること"""
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1 AS number")
            record = result.single()
            assert record is not None
            assert record["number"] == 1

    def test_server_info(self, neo4j_driver: Driver):
        """サーバー情報が取得できること"""
        info = neo4j_driver.get_server_info()
        assert info is not None
        assert info.agent is not None


@pytest.mark.db
class TestNeo4jGraphStoreManager:
    """Neo4jGraphStoreManager 接続確認テスト"""

    def test_health_check(self):
        """health_check が True を返すこと"""
        manager = Neo4jGraphStoreManager()
        assert manager.health_check() is True

    def test_store_property(self):
        """store プロパティが Neo4jPropertyGraphStore を返すこと"""
        from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

        manager = Neo4jGraphStoreManager()
        store = manager.store
        assert isinstance(store, Neo4jPropertyGraphStore)

    def test_store_is_cached(self):
        """store プロパティが同一インスタンスを返すこと（遅延初期化キャッシュ）"""
        manager = Neo4jGraphStoreManager()
        assert manager.store is manager.store
