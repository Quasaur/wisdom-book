
from django.test import TestCase
from unittest.mock import MagicMock, patch
from .models import Quote
from topics_app.models import Topic
from .services import quotes_service

class QuotesSyncTests(TestCase):
    def setUp(self):
        # Create a parent topic
        self.topic = Topic.objects.create(
            neo4j_id="topic_1",
            title="Wisdom",
            level=1
        )
        
    def test_sync_quotes_with_parent(self):
        """Test syncing a quote that has a parent topic"""
        
        # Mock Neo4j response
        mock_data = [{
            'id': 'quote_1',
            'title': 'Test Quote',
            'author': 'Tester',
            'level': 2,
            'source': 'Test Source',
            'book_link': '',
            'parent_id': 'topic_1',
            'tags': ['test'],
            'contents': []
        }]
        
        # Patch the neo4j instance on the global service object
        with patch.object(quotes_service.neo4j, 'run_query', return_value=mock_data):
            # Run sync
            success, message, count = quotes_service.sync_quotes_from_neo4j()
            
            # Verify result
            self.assertTrue(success)
            self.assertEqual(count, 1)
            
            # Verify Database
            quote = Quote.objects.get(neo4j_id='quote_1')
            self.assertEqual(quote.title, 'Test Quote')
            self.assertEqual(quote.level, 2)
            self.assertEqual(quote.parent, self.topic)
        
    def test_sync_quotes_missing_parent(self):
        """Test syncing a quote where parent topic doesn't exist locally"""
        
        mock_data = [{
            'id': 'quote_2',
            'title': 'Orphan Quote',
            'parent_id': 'missing_topic',
            'level': 1
        }]
        
        with patch.object(quotes_service.neo4j, 'run_query', return_value=mock_data):
            # Run sync
            quotes_service.sync_quotes_from_neo4j()
            
            # Verify Database
            quote = Quote.objects.get(neo4j_id='quote_2')
            self.assertIsNone(quote.parent)
