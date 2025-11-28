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
from .middleware.query_logger import log_query

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Add a custom exception for Neo4j query errors with context
class Neo4jQueryError(Exception):
    """Enhanced exception for Neo4j queries with context and guidance"""
    
    def __init__(self, message: str, query_name: str = "unnamed", 
                 cypher: Optional[str] = None, params: Optional[Dict] = None,
                 guidance: Optional[str] = None):
        self.query_name = query_name
        self.cypher = cypher
        self.params = params
        self.guidance = guidance
        
        # Build detailed message
        details = [message]
        details.append(f"Query: {query_name}")
        
        if cypher:
            # Format the query for better readability
            formatted_query = "\n    ".join(cypher.strip().split("\n"))
            details.append(f"Cypher:\n    {formatted_query}")
            
        if params:
            # Redact potential sensitive parameters
            safe_params = {k: (v if k.lower() not in ('password', 'secret', 'token', 'key') else '[REDACTED]') 
                          for k, v in params.items()}
            details.append(f"Params: {safe_params}")
            
        if guidance:
            details.append(f"Guidance:\n{guidance}")
            
        super().__init__("\n".join(details))

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

    @log_query
    def run_query(
        self,
        cypher: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        query_name: str = "unnamed_query",
        write: bool = False,
        max_retries: int = 3,
        retry_backoff: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        Retries only safe (non-writing) operations on transient errors.
        
        Args:
            cypher: The Cypher query to execute
            params: Query parameters
            query_name: Name of query for better error messages
            write: Is this a write operation? (no retries if True)
            max_retries: Maximum retry attempts
            retry_backoff: Backoff multiplier for retries
            
        Returns:
            List of result records as dictionaries
            
        Raises:
            Neo4jQueryError: Wrapper with enhanced context for all Neo4j errors
        """
        attempt = 0
        while True:
            try:
                with self._open_session() as session:
                    result = session.run(cypher, params or {})
                    return [r.data() for r in result]
            except (SessionExpired, TransientError, ServiceUnavailable) as e:
                if write:
                    logger.error("Write query %r failed (no retry): %s", query_name, e)
                    raise Neo4jQueryError(f"Write operation failed: {e}", 
                                        query_name=query_name, 
                                        cypher=cypher,
                                        params=params) from e
                attempt += 1
                if attempt > max_retries:
                    logger.error("Exceeded retries for query %r: %s", query_name, cypher)
                    raise Neo4jQueryError(f"Max retries exceeded: {e}", 
                                        query_name=query_name, 
                                        cypher=cypher,
                                        params=params) from e
                sleep_for = retry_backoff * (2 ** (attempt - 1))
                logger.warning("Transient error (%s) in query %r. Retry %d/%d in %.2fs",
                               e.__class__.__name__, query_name, attempt, max_retries, sleep_for)
                time.sleep(sleep_for)
            except neo4j.exceptions.CypherSyntaxError as e:
                # Extract line and column from error message
                error_msg = str(e)
                syntax_guidance = self._get_syntax_guidance(error_msg)
                
                logger.error("Cypher syntax error in query %r: %s\n%s", 
                           query_name, e, syntax_guidance)
                
                raise Neo4jQueryError(
                    f"Syntax error: {e}",
                    query_name=query_name,
                    cypher=cypher,
                    params=params,
                    guidance=syntax_guidance
                ) from e
            except AuthError as e:
                logger.exception("Authentication failed to Neo4j during query %r", query_name)
                raise Neo4jQueryError("Authentication failed", 
                                    query_name=query_name, 
                                    cypher=cypher) from e
            except Exception as e:
                logger.exception("Unexpected Neo4j error in query %r", query_name)
                raise Neo4jQueryError(f"Unexpected error: {e}", 
                                    query_name=query_name, 
                                    cypher=cypher,
                                    params=params) from e

    def _get_syntax_guidance(self, error_msg: str) -> str:
        """Provide guidance for common syntax errors based on error message"""
        guidance = []
        
        # Add specific guidance based on error patterns
        if "exists(variable.property)" in error_msg:
            guidance.append(
                "SYNTAX UPDATE REQUIRED: Replace 'exists(n.property)' with 'n.property IS NOT NULL'\n"
                "Example: WHERE exists(n.name) -> WHERE n.name IS NOT NULL"
            )
        
        if "STARTS WITH" in error_msg or "ENDS WITH" in error_msg or "CONTAINS" in error_msg:
            guidance.append(
                "Check case sensitivity in string operations (STARTS WITH, ENDS WITH, CONTAINS).\n"
                "These are case-sensitive by default. Use toLower() for case-insensitive matching."
            )
            
        if "MATCH (n)-[r]->" in error_msg:
            guidance.append(
                "Check relationship direction. If not specific, use (n)-[r]-(m) for undirected matching."
            )
            
        if "Error 42I52" in error_msg:
            guidance.append(
                "Neo4j 5.x compatibility issue: Ensure your Cypher syntax is compatible with Neo4j 5+."
            )
            
        # Add general guidance if no specific matches
        if not guidance:
            guidance.append(
                "General tips:\n"
                "- Check property names and case sensitivity\n"
                "- Verify all parentheses are balanced\n"
                "- Use parametrized queries instead of string concatenation\n"
                "- Refer to Neo4j 5.x Cypher documentation for latest syntax"
            )
            
        return "\n".join(guidance)



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
        count_result = self.run_query(
            "MATCH (t:TOPIC) RETURN count(t) AS total",
            query_name="topics_count"
        )
        total = count_result[0]["total"] if count_result else 0
        data = self.run_query(
            """
            MATCH (t:TOPIC)
            RETURN t.name AS name, t.alias AS alias, t.tags AS tags
            ORDER BY toLower(name)
            SKIP $skip LIMIT $limit
            """,
            {"skip": skip, "limit": limit},
            query_name="topics_list"
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
            query_name="search_content_count"
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
            query_name="search_content_results"
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
        AND any(l IN labels(item) WHERE l IN ['TOPIC', 'THOUGHT', 'QUOTE', 'PASSAGE'])
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