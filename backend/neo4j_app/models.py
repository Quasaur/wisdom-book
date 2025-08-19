from django.db import models

# Create your models here.

class VirtualLogEntry:
    """
    Virtual model representing a Neo4j query log entry.
    Not stored in the database - parsed from log files on demand.
    """
    def __init__(self, timestamp=None, level=None, message=None, 
                 query_name=None, duration_ms=None, is_slow=False,
                 query_text=None, error=None, context=None, path=None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.query_name = query_name
        self.duration_ms = duration_ms
        self.is_slow = is_slow
        self.query_text = query_text
        self.error = error
        self.context = context or {}
        self.path = path
        
    def __str__(self):
        return f"{self.timestamp} - {self.query_name} - {self.duration_ms}ms"
    
    @property
    def has_error(self):
        return self.level == 'ERROR' or self.error is not None
    
    @property
    def solution(self):
        """Returns a suggested solution based on error patterns"""
        if not self.has_error:
            return None
            
        error_text = self.error or self.message or ""
        
        # Common error patterns and solutions
        if "exists(variable.property)" in error_text:
            return {
                "title": "Deprecated Syntax - Property Existence Check",
                "description": "The `exists()` function is no longer supported in Neo4j 5+",
                "solution": "Replace `exists(n.property)` with `n.property IS NOT NULL`",
                "example": """
# Before
MATCH (n) WHERE exists(n.name) RETURN n

# After
MATCH (n) WHERE n.name IS NOT NULL RETURN n
"""
            }
        elif "CONTAINS" in error_text and "case" in error_text.lower():
            return {
                "title": "Case-Sensitive String Matching",
                "description": "String operations are case-sensitive by default",
                "solution": "Use toLower() for case-insensitive matching",
                "example": """
# Before (case-sensitive)
WHERE n.name CONTAINS 'text'

# After (case-insensitive)
WHERE toLower(n.name) CONTAINS toLower($text)
"""
            }
        elif "no such index" in error_text.lower() or "could not resolve the referenced property" in error_text.lower():
            return {
                "title": "Missing Index or Property",
                "description": "Query references a property that isn't indexed or doesn't exist",
                "solution": "Create the appropriate index or check property name",
                "example": """
# Check property existence
MATCH (n:TOPIC) WHERE n.name = 'Example' RETURN n LIMIT 1

# Create index if needed
CREATE INDEX topic_name_index IF NOT EXISTS FOR (t:TOPIC) ON (t.name)
"""
            }
        elif "timeout" in error_text.lower() or "deadlock" in error_text.lower():
            return {
                "title": "Query Timeout or Deadlock",
                "description": "Query took too long or encountered lock contention",
                "solution": "Optimize the query with more specific patterns, add LIMIT, or use EXPLAIN/PROFILE",
                "example": """
# Run EXPLAIN to see query plan
EXPLAIN MATCH (n)-[r]-(m) RETURN n, r, m

# Add more specific patterns and limits
MATCH (n:TOPIC)-[r:HAS_CHILD]->(m) 
RETURN n, r, m LIMIT 100
"""
            }
        
        # Generic solution for unrecognized errors
        return {
            "title": "Unrecognized Error Pattern",
            "description": "This error doesn't match common patterns",
            "solution": "Check Neo4j logs and documentation for more details",
            "example": f"Error message: {error_text}"
        }
