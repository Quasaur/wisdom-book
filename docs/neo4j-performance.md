# Neo4j Performance Monitoring

This document covers performance monitoring tools and best practices for Neo4j queries in the Wisdom Book application.

## Slow Query Logging

The application includes an automated system for logging and analyzing slow Neo4j queries to help identify performance bottlenecks.

### How It Works

1. Each Neo4j query is automatically timed.
2. Queries exceeding a configurable threshold (default: 100ms) are logged.
3. Query details including parameters and execution context are captured.
4. Analysis tools help identify patterns in slow queries.

### Configuration

Configure the slow query logging in Django settings:

```python
# settings.py
NEO4J_QUERY_LOGGING = {
    'slow_query_threshold_ms': 100,  # Log queries taking longer than 100ms
    'log_all_queries': False,        # When True, log all queries regardless of time
    'log_to_file': True,             # Whether to log to a separate file
    'log_file': 'logs/neo4j_slow_queries.log',  # Log file path
    'include_params': True,          # Include query parameters in log
    'include_results': False,        # Include result summary in log
    'redact_fields': ['password', 'token', 'secret', 'key'],  # Fields to redact
}
```

### Analyzing Slow Queries

Use the management command to analyze the slow query log:

```bash
# Show top 10 slowest queries
python manage.py analyze_neo4j_queries

# Change minimum time threshold
python manage.py analyze_neo4j_queries --min-time=500

# Group by API endpoint instead of query name
python manage.py analyze_neo4j_queries --group-by=request_path

# Export as JSON
python manage.py analyze_neo4j_queries --output=json > slow_queries.json
```

### Programmatic Access

You can also access slow query stats programmatically:

```python
from neo4j_app.middleware.query_logger import get_slow_query_stats

# Get stats for the 5 slowest query types
stats = get_slow_query_stats(top_n=5)

# Process the stats
for stat in stats:
    print(f"Query: {stat['name']}")
    print(f"Average time: {stat['avg_time_ms']:.2f}ms")
    print(f"Call count: {stat['count']}")
```

## Common Performance Issues

### 1. Missing Indexes

Neo4j performs best when appropriate indexes exist for properties used in WHERE clauses.

```cypher
# Check existing indexes
SHOW INDEXES

# Create index for commonly queried properties
CREATE INDEX topic_name IF NOT EXISTS FOR (t:TOPIC) ON (t.name)
```

### 2. Complex Pattern Matching

Large pattern matches without limits can cause performance issues:

```cypher
# Instead of unbounded traversal:
MATCH (t:TOPIC)-[*]-(n)  # BAD: unbounded depth

# Use bounded depth:
MATCH (t:TOPIC)-[*1..3]-(n)  # BETTER: limited depth

# Even better, paginate results:
MATCH (t:TOPIC)-[*1..3]-(n)
RETURN n
SKIP $skip LIMIT $limit
```

### 3. Property Existence Checks

Use `IS NOT NULL` instead of `exists()`:

```cypher
# Instead of:
WHERE exists(n.name)  # Deprecated in Neo4j 5+

# Use:
WHERE n.name IS NOT NULL
```

### 4. Case-sensitive String Operations

Use `toLower()` for case-insensitive matching:

```cypher
# Instead of case-sensitive match:
WHERE n.name CONTAINS "wisdom"

# Use case-insensitive:
WHERE toLower(n.name) CONTAINS toLower($term)
```

## Interpreting Slow Query Logs

Example log entry:
```
2023-05-14 15:30:12,123 [WARNING] Neo4j Query: search_content (SLOW) - 345.67ms - MATCH (n) WHERE...
```

This tells you:
- When the query ran
- The query name ("search_content")
- That it was flagged as slow
- The execution time (345.67ms)
- The beginning of the query

The logs contain more detailed information in JSON format that can be analyzed with the command-line tool.

## Next Steps for Optimization

1. **Index Coverage**: Ensure all frequently queried properties have indexes.
2. **Query Refactoring**: Restructure queries frequently appearing in the slow query log.
3. **Result Caching**: Consider caching results for expensive queries that don't change often.
4. **Pattern Analysis**: Look for patterns in slow queries (time of day, user actions, etc.).
