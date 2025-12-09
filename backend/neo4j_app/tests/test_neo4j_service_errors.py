import unittest
from unittest.mock import patch, MagicMock, call
import time
import pytest

from neo4j.exceptions import (
    ServiceUnavailable, 
    AuthError, 
    SessionExpired, 
    TransientError, 
    CypherSyntaxError
)

from neo4j_app.neo4j_service import Neo4jService, Neo4jQueryError


class TestNeo4jServiceErrorHandling(unittest.TestCase):
    """Test suite for Neo4j error handling in Neo4jService."""
    
    def setUp(self):
        # Reset the driver for each test
        self.service = Neo4jService()
        self.service._driver = None
        
        # Common testing query and params
        self.test_query = "MATCH (n) RETURN n LIMIT 1"
        self.test_params = {"param1": "value1"}

    def test_neo4j_query_error_formatting(self):
        """Test that Neo4jQueryError includes useful context in its message."""
        error = Neo4jQueryError(
            message="Test error message",
            query_name="test_query",
            cypher="MATCH (n) RETURN n",
            params={"test": "value"},
            guidance="Use better Cypher"
        )
        
        error_str = str(error)
        # Verify all important parts are in the formatted error
        self.assertIn("Test error message", error_str)
        self.assertIn("test_query", error_str)
        self.assertIn("MATCH (n) RETURN n", error_str)
        self.assertIn("test", error_str)
        self.assertIn("value", error_str)
        self.assertIn("Use better Cypher", error_str)
        
    def test_neo4j_query_error_redacts_sensitive_params(self):
        """Test that Neo4jQueryError redacts sensitive parameters."""
        error = Neo4jQueryError(
            message="Auth failed",
            query_name="auth_query",
            params={"username": "neo4j", "password": "secret"}
        )
        
        error_str = str(error)
        self.assertIn("username", error_str)
        self.assertIn("neo4j", error_str)
        self.assertNotIn("secret", error_str)
        self.assertIn("[REDACTED]", error_str)

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    def test_authentication_error_handling(self, mock_graph_db):
        """Test that AuthError is properly caught and wrapped."""
        # Setup mock to raise AuthError
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = AuthError("Invalid credentials")
        
        # Call method and check exception
        with self.assertRaises(Neo4jQueryError) as cm:
            self.service.run_query(self.test_query, self.test_params)
            
        # Verify the error is properly wrapped
        self.assertIn("Authentication failed", str(cm.exception))
        self.assertIn(self.test_query, str(cm.exception))

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    @patch('neo4j_app.neo4j_service.time.sleep')
    def test_transient_error_retry_success(self, mock_sleep, mock_graph_db):
        """Test retry logic works for transient errors."""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # First call fails with TransientError, second succeeds
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        # Create a side effect that raises TransientError once, then returns a value
        mock_result = MagicMock()
        mock_result.data.return_value = {"key": "value"}
        
        # First call raises TransientError, second call returns mock_result
        # First call raises TransientError, second call returns mock_result
        mock_session.run.side_effect = [
            TransientError("Temporary failure"),
            [mock_result]
        ]
        
        # Call method
        result = self.service.run_query(self.test_query, self.test_params)
        
        # Verify retry happened
        self.assertEqual(mock_session.run.call_count, 2)
        mock_sleep.assert_called_once()
        self.assertEqual(result, [{"key": "value"}])

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    @patch('neo4j_app.neo4j_service.time.sleep')
    def test_transient_error_max_retries_exceeded(self, mock_sleep, mock_graph_db):
        """Test that max retries are enforced for transient errors."""
        # Setup mock to always raise TransientError
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = TransientError("Persistent temporary failure")
        
        # Call method with fewer retries for test speed
        with self.assertRaises(Neo4jQueryError) as cm:
            self.service.run_query(self.test_query, self.test_params, max_retries=2)
            
        # Verify the correct number of retries occurred
        self.assertEqual(mock_session.run.call_count, 3)  # Initial + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)
        self.assertIn("Max retries exceeded", str(cm.exception))

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    def test_cypher_syntax_error_handling(self, mock_graph_db):
        """Test that CypherSyntaxError is caught and wrapped with guidance."""
        # Setup mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        # Create a syntax error mentioning exists() function which should trigger guidance
        syntax_error = CypherSyntaxError(
            "The property existence syntax `exists(variable.property)` is no longer supported."
        )
        mock_session.run.side_effect = syntax_error
        
        # Call method and check exception
        with self.assertRaises(Neo4jQueryError) as cm:
            self.service.run_query(self.test_query, self.test_params)
            
        # Verify the error message contains guidance
        self.assertIn("Syntax error", str(cm.exception))
        self.assertIn("SYNTAX UPDATE REQUIRED", str(cm.exception))
        self.assertIn("Replace 'exists(n.property)' with 'n.property IS NOT NULL'", str(cm.exception))

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    def test_write_query_no_retry(self, mock_graph_db):
        """Test that write queries don't retry on transient errors."""
        # Setup mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = TransientError("Temporary failure")
        
        # Call method with write=True
        with self.assertRaises(Neo4jQueryError) as cm:
            self.service.run_query(self.test_query, self.test_params, write=True)
            
        # Verify no retry was attempted (only one call)
        self.assertEqual(mock_session.run.call_count, 1)
        self.assertIn("Write operation failed", str(cm.exception))

    @patch('neo4j_app.neo4j_service.GraphDatabase')
    def test_unexpected_error_handling(self, mock_graph_db):
        """Test handling of unexpected errors."""
        # Setup mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = ValueError("Unexpected error")
        
        # Call method and check exception
        with self.assertRaises(Neo4jQueryError) as cm:
            self.service.run_query(self.test_query, self.test_params)
            
        # Verify the error message contains original error
        self.assertIn("Unexpected error", str(cm.exception))
        self.assertIn(self.test_query, str(cm.exception))

    def test_get_syntax_guidance_for_exists(self):
        """Test that appropriate guidance is provided for exists() syntax errors."""
        error_msg = "The property existence syntax `exists(variable.property)` is no longer supported."
        guidance = self.service._get_syntax_guidance(error_msg)
        
        self.assertIn("SYNTAX UPDATE REQUIRED", guidance)
        self.assertIn("Replace 'exists(n.property)' with 'n.property IS NOT NULL'", guidance)

    def test_get_syntax_guidance_for_string_operations(self):
        """Test that appropriate guidance is provided for string operation errors."""
        error_msg = "Error with CONTAINS operation in Neo4j."
        guidance = self.service._get_syntax_guidance(error_msg)
        
        self.assertIn("Check case sensitivity", guidance)
        self.assertIn("toLower()", guidance)


# Create separate pytest-style fixtures for more complex tests
@pytest.fixture
def mock_neo4j_service():
    """Fixture to provide a Neo4jService instance with mocked driver."""
    with patch('neo4j_app.neo4j_service.GraphDatabase') as mock_graph_db:
        service = Neo4jService()
        
        # Configure the mock
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Attach the mock driver to make it accessible in tests
        service._driver = mock_driver
        
        yield service, mock_driver


@pytest.mark.django_db
def test_health_method_handles_errors(mock_neo4j_service):
    """Test that health() method properly handles errors and returns False."""
    service, mock_driver = mock_neo4j_service
    
    # Setup session mock to raise exception
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.run.side_effect = ServiceUnavailable("Service unavailable")
    
    # health() should return False on any error
    assert service.health() is False
    
    # health() should not propagate errors
    mock_session.run.assert_called_once()
