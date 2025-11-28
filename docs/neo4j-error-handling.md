# Neo4j Error Handling Guide

This document outlines common Neo4j errors and solutions to help developers troubleshoot issues.

## Common Cypher Syntax Errors

### Property Existence Syntax

**Error:** `Neo4jError: ...` (Generic error)

**Solution:**
Check the application logs for the full stack trace. The `Neo4jQueryError` wrapper provides additional context, including the query name, parameters (redacted), and specific guidance for common issues.

### 1. Syntax Errors

**Common Causes:**
- Invalid Cypher syntax.
- Using deprecated functions (e.g., `exists()` in Neo4j 5+).
- Mismatched parentheses or brackets.

**Solution:**
- Review the `Guidance` section in the error log.
- Use `IS NOT NULL` instead of `exists()`.
- Ensure all brackets are balanced.

### 2. Authentication Errors

**Common Causes:**
- Incorrect `NEO4J_URI`, `NEO4J_USERNAME`, or `NEO4J_PASSWORD` in `.env`.
- Database user is locked or password has expired.

**Solution:**
- Verify credentials in the `.env` file.
- Check connectivity to the Neo4j instance using a separate tool (e.g., Neo4j Browser).

### 3. Transient Errors

**Common Causes:**
- Temporary network glitches.
- Database leader switching in a cluster.

**Solution:**
- The `Neo4jService` automatically retries read operations on transient errors.
- For write operations, ensure your application logic can handle potential failures or retries at a higher level.

## Debugging Tips

1. **Check the Logs:** The `neo4j_slow_queries.log` (if enabled) and standard application logs contain detailed information about failed queries.
2. **Isolate the Query:** Copy the Cypher query from the log (formatted for readability) and run it in the Neo4j Browser to reproduce the issue.
3. **Check Parameters:** Ensure that the parameters passed to the query match the expected types and values.
