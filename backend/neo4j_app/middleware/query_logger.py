"""
Neo4j query logger for tracking and analyzing slow Cypher queries.
"""
import time
import logging
import json
import os
import threading
from functools import wraps
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

# Set up dedicated logger for queries
query_logger = logging.getLogger("neo4j.queries")

# Default configuration
DEFAULT_CONFIG = {
    "slow_query_threshold_ms": 100,  # Log queries taking longer than 100ms
    "log_all_queries": False,        # When True, log all queries regardless of time
    "log_to_file": True,             # Whether to log to a separate file
    "log_file": "neo4j_slow_queries.log",  # Log file path (relative to project root)
    "include_params": True,          # Include query parameters in log
    "include_results": False,        # Include result summary in log
    "redact_fields": ["password", "token", "secret", "key"],  # Fields to redact in params
}

# Thread-local storage for request context
_local = threading.local()

class QueryLoggerMiddleware:
    """
    Django middleware to add request info to query logs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request info in thread-local for logging context
        _local.request_path = request.path
        _local.request_method = request.method
        _local.request_id = request.headers.get('X-Request-ID', '')
        _local.user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') else None
        
        # Process request and response as usual
        response = self.get_response(request)
        
        # Clean up thread-local to prevent memory leaks
        if hasattr(_local, 'request_path'):
            del _local.request_path
        if hasattr(_local, 'request_method'):
            del _local.request_method
        if hasattr(_local, 'request_id'):
            del _local.request_id
        if hasattr(_local, 'user_id'):
            del _local.user_id
            
        return response

def configure_query_logging(config: Dict[str, Any] = None) -> None:
    """
    Configure the query logger settings.
    
    Args:
        config: Dictionary of configuration options to override defaults.
    """
    effective_config = {**DEFAULT_CONFIG, **(config or {})}
    
    # Set up file handler if enabled
    if effective_config["log_to_file"]:
        # Determine the log file path
        log_file = effective_config["log_file"]
        if not os.path.isabs(log_file):
            # Try to find project root for relative paths
            if "DJANGO_SETTINGS_MODULE" in os.environ:
                # Get base dir from Django settings
                from django.conf import settings
                base_dir = getattr(settings, "BASE_DIR", None)
                if base_dir:
                    log_file = os.path.join(base_dir, log_file)
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to create log directory '{log_dir}': {e}")
            # Fallback to a file in the current directory if we can't create the intended directory
            log_file = "neo4j_slow_queries.log"
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        query_logger.addHandler(file_handler)
    
    # Ensure the logger level is set appropriately
    query_logger.setLevel(logging.INFO)
    
    # Store config for later access
    query_logger.config = effective_config

def log_query(func):
    """
    Decorator for logging Neo4j queries and their execution time.
    
    Usage:
        @log_query
        def run_query(self, cypher, params=None, **kwargs):
            # existing implementation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get config or use defaults
        config = getattr(query_logger, "config", DEFAULT_CONFIG)
        
        # Extract query info from args/kwargs
        cypher = args[1] if len(args) > 1 else kwargs.get("cypher", "")
        params = args[2] if len(args) > 2 else kwargs.get("params", {})
        query_name = kwargs.get("query_name", "unnamed")
        write_operation = kwargs.get("write", False)
        
        # Prepare redacted params if needed
        if config["include_params"] and params:
            if isinstance(params, dict):
                redacted_params = {
                    k: "[REDACTED]" if any(field.lower() in k.lower() 
                                          for field in config["redact_fields"]) 
                                     else v
                    for k, v in params.items()
                }
            else:
                redacted_params = params
        else:
            redacted_params = None
        
        # Build context dictionary for logging
        context = {
            "query_name": query_name,
            "write_operation": write_operation,
            "params": redacted_params if config["include_params"] else None,
        }
        
        # Add request context if available (from middleware)
        if hasattr(_local, 'request_path'):
            context["request_path"] = getattr(_local, 'request_path', None)
            context["request_method"] = getattr(_local, 'request_method', None)
            context["request_id"] = getattr(_local, 'request_id', None)
            context["user_id"] = getattr(_local, 'user_id', None)
        
        # Measure execution time
        start_time = time.time()
        
        try:
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Calculate elapsed time
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Add execution time to context
            context["elapsed_ms"] = elapsed_ms
            context["success"] = True
            
            # Include result info if configured
            if config["include_results"] and result:
                context["result_count"] = len(result) if isinstance(result, list) else 1
            
            # Check if this is a slow query
            is_slow = elapsed_ms > config["slow_query_threshold_ms"]
            
            # Log if it's slow or if we're logging all queries
            if is_slow or config["log_all_queries"]:
                # Create short version of query (first line or truncated)
                short_query = cypher.split('\n')[0][:80] + ('...' if len(cypher) > 80 else '')
                
                # Determine log level based on performance
                log_level = logging.WARNING if is_slow else logging.INFO
                
                # Log the query
                log_message = (
                    f"Neo4j Query: {query_name} {'(SLOW)' if is_slow else ''} - "
                    f"{elapsed_ms:.2f}ms - {short_query}"
                )
                
                query_logger.log(log_level, log_message, extra={"context": context})
                
                # For very slow queries, also log the full query
                if elapsed_ms > config["slow_query_threshold_ms"] * 5:
                    query_logger.warning(f"Full slow query:\n{cypher}")
            
            return result
            
        except Exception as e:
            # Calculate elapsed time for failed query
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Add error info to context
            context["elapsed_ms"] = elapsed_ms
            context["success"] = False
            context["error"] = str(e)
            context["error_type"] = e.__class__.__name__
            
            # Log the error with query context
            log_message = f"Neo4j Query Error: {query_name} - {elapsed_ms:.2f}ms - {str(e)}"
            query_logger.error(log_message, extra={"context": context})
            
            # Re-raise the exception
            raise
            
    return wrapper

def get_slow_query_stats(log_file=None, min_time_ms=None, 
                         group_by="query_name", top_n=10) -> List[Dict[str, Any]]:
    """
    Parse the slow query log and return statistics.
    
    Args:
        log_file: Path to the log file (uses configured file if None)
        min_time_ms: Minimum query time to include (uses configured threshold if None)
        group_by: Field to group queries by ("query_name", "path", etc.)
        top_n: Number of top slowest queries to return
        
    Returns:
        List of dictionaries with query statistics.
    """
    config = getattr(query_logger, "config", DEFAULT_CONFIG)
    
    # Use configured values as defaults
    if log_file is None:
        log_file = config["log_file"]
    
    if min_time_ms is None:
        min_time_ms = config["slow_query_threshold_ms"]
    
    # Check if log file exists
    if not os.path.exists(log_file):
        return []
    
    stats = {}
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Try to extract the JSON context
                try:
                    if '"context":' in line:
                        context_str = line.split('"context":')[1].strip()
                        # Handle the case where there might be more JSON after context
                        if context_str.endswith('}'):
                            context_str = context_str[:-1]
                        context = json.loads(context_str)
                        
                        # Skip if below threshold
                        if context.get("elapsed_ms", 0) < min_time_ms:
                            continue
                        
                        # Get the group key
                        group_key = context.get(group_by, "unknown")
                        
                        # Initialize group if needed
                        if group_key not in stats:
                            stats[group_key] = {
                                "count": 0,
                                "total_time_ms": 0,
                                "avg_time_ms": 0,
                                "max_time_ms": 0,
                                "min_time_ms": float('inf'),
                                "last_occurred": None,
                                "examples": []
                            }
                        
                        # Update stats
                        elapsed = context.get("elapsed_ms", 0)
                        stats[group_key]["count"] += 1
                        stats[group_key]["total_time_ms"] += elapsed
                        stats[group_key]["avg_time_ms"] = (
                            stats[group_key]["total_time_ms"] / stats[group_key]["count"]
                        )
                        stats[group_key]["max_time_ms"] = max(
                            stats[group_key]["max_time_ms"], elapsed
                        )
                        stats[group_key]["min_time_ms"] = min(
                            stats[group_key]["min_time_ms"], elapsed
                        )
                        
                        # Update timestamp from log entry
                        timestamp_str = line.split(' [')[0]
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                            stats[group_key]["last_occurred"] = timestamp.isoformat()
                        except ValueError:
                            pass
                        
                        # Store example if it's one of the slowest
                        if len(stats[group_key]["examples"]) < 3:
                            stats[group_key]["examples"].append(context)
                        elif elapsed > stats[group_key]["examples"][-1].get("elapsed_ms", 0):
                            stats[group_key]["examples"][-1] = context
                            # Sort examples by elapsed time (descending)
                            stats[group_key]["examples"].sort(
                                key=lambda x: x.get("elapsed_ms", 0),
                                reverse=True
                            )
                except Exception:
                    # Skip malformed lines
                    continue
    except Exception as e:
        query_logger.error(f"Error parsing slow query log: {e}")
    
    # Convert to list and sort by average time
    result = [{"name": k, **v} for k, v in stats.items()]
    result.sort(key=lambda x: x["avg_time_ms"], reverse=True)
    
    # Return top N results
    return result[:top_n]
