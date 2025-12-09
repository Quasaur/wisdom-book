from django.test import TestCase
from unittest.mock import patch, MagicMock
from topics_app.services import TopicsService
from topics_app.models import Topic

class SyncIntegrityTests(TestCase):
    def setUp(self):
        self.service = TopicsService()

    @patch('topics_app.services.neo4j_service.run_query')
    def test_sync_filters_phantom_topics(self, mock_run_query):
        """
        Test that topics NOT starting with 'Topic: ' are filtered out during sync.
        """
        # Mock Neo4j response with one valid topic and one phantom topic
        mock_data = [
            {
                'id': 'topic.VALID',
                'title': 'Topic: Valid Name',
                'description': 'A valid topic.',
                'level': 1,
                'parent': 'topic.ROOT',
                'tags': ['valid'],
                'descriptions': []
            },
            {
                'id': 'topic.PHANTOM',
                'title': 'Life', # Does not start with "Topic: "
                'description': 'A phantom topic.',
                'level': 1,
                'parent': 'topic.ROOT',
                'tags': ['phantom'],
                'descriptions': []
            }
        ]
        
        # Configure mock to return this data
        mock_run_query.return_value = mock_data
        
        # Run sync
        success, msg, count = self.service.sync_topics_from_neo4j(force=True)
        
        # Assertions
        self.assertTrue(success)
        
        # Valid topic should exist
        self.assertTrue(Topic.objects.filter(neo4j_id='topic.VALID').exists())
        
        # Phantom topic should NOT exist
        self.assertFalse(Topic.objects.filter(neo4j_id='topic.PHANTOM').exists())
        
        # Count should reflect what was actually saved (or processed? method returns processed count)
        # Note: Depending on implementation, count might include filtered ones or not. 
        # For now, we mainly care about DB state.

    @patch('topics_app.services.neo4j_service.run_query')
    def test_topic_zero_allowed(self, mock_run_query):
        """
        Test that 'Topic ZERO: THE NULL TOPIC' is allowed.
        """
        mock_data = [
            {
                'id': 'topic.ZERO',
                'title': 'Topic ZERO: THE NULL TOPIC',
                'description': 'The null topic',
                'level': 0,
                'parent': None,
                'tags': ['zero'],
                'descriptions': []
            }
        ]
        mock_run_query.return_value = mock_data
        
        self.service.sync_topics_from_neo4j(force=True)
        
        # Should populate
        self.assertTrue(Topic.objects.filter(neo4j_id='topic.ZERO').exists())
