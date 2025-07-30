from django.test import TestCase
from django.conf import settings
from .neo4j_service import Neo4jService
import logging

logger = logging.getLogger(__name__)


class Neo4jConnectionTest(TestCase):
    """Test Neo4j connection and basic functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = Neo4jService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.service.close()
    
    def test_connection(self):
        """Test that we can connect to Neo4j"""
        try:
            # Test a simple query
            result = self.service.run_query("RETURN 1 as test")
            self.assertEqual(result[0]['test'], 1)
            logger.info("Neo4j connection test passed")
        except Exception as e:
            logger.error(f"Neo4j connection test failed: {e}")
            self.fail(f"Failed to connect to Neo4j: {e}")
    
    def test_get_all_topics(self):
        """Test getting topics from Neo4j"""
        try:
            topics = self.service.get_all_topics(limit=5)
            self.assertIsInstance(topics, list)
            logger.info(f"Successfully retrieved {len(topics)} topics")
        except Exception as e:
            logger.error(f"Failed to get topics: {e}")
            self.fail(f"Failed to get topics: {e}")
    
    def test_search_content(self):
        """Test searching content"""
        try:
            results = self.service.search_content("love", limit=5)
            self.assertIsInstance(results, list)
            logger.info(f"Search returned {len(results)} results")
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            self.fail(f"Search test failed: {e}")


class Neo4jViewsTest(TestCase):
    """Test Neo4j API views"""
    
    def test_topics_list_view(self):
        """Test topics list API endpoint"""
        response = self.client.get('/api/neo4j/topics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
    
    def test_search_view(self):
        """Test search API endpoint"""
        response = self.client.get('/api/neo4j/search/?q=love')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
    
    def test_search_view_no_query(self):
        """Test search API endpoint with no query"""
        response = self.client.get('/api/neo4j/search/')
        self.assertEqual(response.status_code, 400)
