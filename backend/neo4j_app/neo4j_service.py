import os
import time
import logging
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    SessionExpired,
    TransientError,
)

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

class Neo4jService:
    """
    Lazy-initialized Neo4j driver wrapper with:
    - Explicit database selection
    - Retry logic for transient read operations
    """

    _driver: Optional[Driver] = None
    _lock = RLock()

    def get_driver(self) -> Driver:
        if self._driver:
            return self._driver
        with self._lock:
            if self._driver:
                return self._driver
            if not (NEO4J_URI and NEO4J_USERNAME):
                raise RuntimeError("Neo4j configuration incomplete: set NEO4J_URI/NEO4J_USERNAME")
            logger.debug("Initializing Neo4j driver")
            self._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
            )
            return self._driver

    def close(self):
        if self._driver:
            try:
                self._driver.close()
            finally:
                self._driver = None

    # ---------- Core execution helpers ----------

    def _open_session(self) -> Session:
        return self.get_driver().session(database=NEO4J_DATABASE)

    def run_query(
        self,
        cypher: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        write: bool = False,
        max_retries: int = 3,
        retry_backoff: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        Retries only safe (non-writing) operations on transient errors.
        """
        attempt = 0
        while True:
            try:
                with self._open_session() as session:
                    result = session.run(cypher, params or {})
                    return [r.data() for r in result]
            except (SessionExpired, TransientError, ServiceUnavailable) as e:
                if write:
                    logger.error("Write query failed (no retry): %s", e)
                    raise
                attempt += 1
                if attempt > max_retries:
                    logger.error("Exceeded retries for query: %s", cypher)
                    raise
                sleep_for = retry_backoff * (2 ** (attempt - 1))
                logger.warning("Transient error (%s). Retry %d/%d in %.2fs",
                               e.__class__.__name__, attempt, max_retries, sleep_for)
                time.sleep(sleep_for)
            except AuthError:
                logger.exception("Authentication failed to Neo4j")
                raise
            except Exception:
                logger.exception("Unexpected Neo4j error")
                raise

    # ---------- Public domain methods ----------

    def health(self) -> bool:
        try:
            res = self.run_query("RETURN 1 AS ok")
            return bool(res and res[0].get("ok") == 1)
        except Exception:
            return False

    def get_all_topics(self, skip: int = 0, limit: int = 25) -> Tuple[List[Dict[str, Any]], int]:
        """
        Return topics plus total count (for pagination).
        """
        count_result = self.run_query("MATCH (t:TOPIC) RETURN count(t) AS total")
        total = count_result[0]["total"] if count_result else 0
        data = self.run_query(
            """
            MATCH (t:TOPIC)
            RETURN t.name AS name, t.alias AS alias, t.tags AS tags
            ORDER BY toLower(name)
            SKIP $skip LIMIT $limit
            """,
            {"skip": skip, "limit": limit},
        )
        return data, total

    def search_content(
        self,
        q: str,
        skip: int = 0,
        limit: int = 25,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Simple case-insensitive substring search across key node labels.
        """
        param = {"q": q}
        count_res = self.run_query(
            """
            MATCH (n)
            WHERE any(l IN labels(n) WHERE l IN ['TOPIC','THOUGHT','QUOTE','PASSAGE'])
              AND (
                (n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($q)) OR
                (n.alias IS NOT NULL AND toLower(n.alias) CONTAINS toLower($q)) OR
                (n.text IS NOT NULL AND toLower(n.text) CONTAINS toLower($q))
              )
            RETURN count(n) AS total
            """,
            param,
        )
        total = count_res[0]["total"] if count_res else 0
        data = self.run_query(
            """
            MATCH (n)
            WHERE any(l IN labels(n) WHERE l IN ['TOPIC','THOUGHT','QUOTE','PASSAGE'])
              AND (
                (n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($q)) OR
                (n.alias IS NOT NULL AND toLower(n.alias) CONTAINS toLower($q)) OR
                (n.text IS NOT NULL AND toLower(n.text) CONTAINS toLower($q))
              )
            RETURN labels(n) AS labels,
                   coalesce(n.name, n.alias, left(n.text, 60)) AS title,
                   n.tags AS tags
            ORDER BY toLower(title)
            SKIP $skip LIMIT $limit
            """,
            {"q": q, "skip": skip, "limit": limit},
        )
        return data, total

    def get_graph_data(self, limit=50):
        """
        Get a subset of nodes and relationships for visualization.
        Returns data formatted for D3.js force-directed graph.
        """
        cypher = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN ['TOPIC', 'THOUGHT', 'QUOTE', 'PASSAGE'])
        WITH n LIMIT $limit
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE any(label IN labels(m) WHERE label IN ['TOPIC', 'THOUGHT', 'QUOTE', 'PASSAGE'])
        WITH collect(DISTINCT {
            id: id(n),
            labels: labels(n),
            name: coalesce(n.name, n.alias, ''),
            type: head(labels(n))
        }) AS nodes,
        collect(DISTINCT {
            source: id(n),
            target: id(m),
            type: type(r)
        }) AS relationships
        RETURN {nodes: nodes, relationships: relationships} AS graph
        """
        result = self.run_query(cypher, {"limit": limit})
        return result[0]["graph"] if result else {"nodes": [], "relationships": []}
    
    def get_tags(self):
        """Get all tags with usage count"""
        query = """
        MATCH (n) WHERE n.tags IS NOT NULL RETURN n.tags AS allTags
        """
        return self.run_query(query)
    
    def get_items_by_tag(self, tag_name, skip=0, limit=20):
        """Get all items with a specific tag (using node properties)"""
        query = """
        MATCH (item)
        WHERE item.tags IS NOT NULL AND $tag_name IN item.tags
        AND (labels(item)[0] = 'TOPIC' OR labels(item)[0] = 'THOUGHT' OR labels(item)[0] = 'QUOTE' OR labels(item)[0] = 'PASSAGE')
        OPTIONAL MATCH (item)-[:HAS_CONTENT]->(content:CONTENT)
        OPTIONAL MATCH (item)-[:HAS_DESCRIPTION]->(desc:DESCRIPTION)
        RETURN item.name as id, item.alias as title, 
               CASE 
                   WHEN content.en_content IS NOT NULL THEN content.en_content
                   WHEN desc.en_content IS NOT NULL THEN desc.en_content
                   WHEN item.notes IS NOT NULL THEN item.notes
                   ELSE ''
               END as content,
               labels(item)[0] as type,
               item.level as level,
               item.tags as tags
        ORDER BY item.level ASC, item.name ASC
        SKIP $skip LIMIT $limit
        """
        return self.run_query(query, {"tag_name": tag_name, "skip": skip, "limit": limit})

# Global service instance
neo4j_service = Neo4jService()