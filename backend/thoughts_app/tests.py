from django.test import TestCase
from unittest.mock import patch, MagicMock
from .services import ThoughtsService
from .models import Thought, Content, ThoughtTag

class ThoughtsSyncTests(TestCase):
    def setUp(self):
        self.service = ThoughtsService()

    @patch('thoughts_app.services.neo4j_service.run_query')
    def test_sync_process_logic(self, mock_run_query):
        """
        Test that sync handles valid thoughts and removes stale ones.
        Note: The filtering of orphans happens in the Cypher query (mocked here),
        so this test verifies that whatever the query returns is synced, and 
        anything else is removed.
        """
        # 1. Create a "stale" thought in DB that should be removed
        Thought.objects.create(
            neo4j_id='thought.STALE',
            title='Stale Thought',
            parent_id='topic.OLD'
        )

        # 2. Mock Neo4j returning only ONE valid thought (implying the other was filtered out or deleted)
        mock_data = [
            {
                'id': 'thought.VALID',
                'title': 'Valid Thought',
                'description': 'A valid thought',
                'en_description': 'A valid thought (en)',
                'tags': ['valid'],
                'parent_id': 'topic.ROOT',
                'contents': []
            }
        ]
        mock_run_query.return_value = mock_data
        
        # 3. Run sync
        success, msg, count = self.service.sync_thoughts_from_neo4j()
        
        # 4. Assertions
        self.assertTrue(success)
        self.assertEqual(count, 1)
        
        # Valid thought should exist
        self.assertTrue(Thought.objects.filter(neo4j_id='thought.VALID').exists())
        valid_thought = Thought.objects.get(neo4j_id='thought.VALID')
        self.assertEqual(valid_thought.parent_id, 'topic.ROOT')
        
        # Stale thought should be GONE
        self.assertFalse(Thought.objects.filter(neo4j_id='thought.STALE').exists())

    @patch('thoughts_app.services.neo4j_service.run_query')
    def test_sync_content_updates(self, mock_run_query):
        """
        Test that content is created and updated correctly.
        """
        mock_data = [
            {
                'id': 'thought.WITH_CONTENT',
                'title': 'Thought with Content',
                'description': 'Desc',
                'parent_id': 'topic.ROOT',
                'tags': [],
                'contents': [
                    {
                        'id': 'content.1',
                        'content': 'Original Content',
                        'en_title': 'Title 1'
                    }
                ]
            }
        ]
        mock_run_query.return_value = mock_data
        
        # Initial sync
        self.service.sync_thoughts_from_neo4j()
        
        # Verify content created
        self.assertTrue(Content.objects.filter(neo4j_id='content.1').exists())
        
        # Update mock data
        mock_data[0]['contents'][0]['content'] = 'Updated Content'
        
        # Sync again
        self.service.sync_thoughts_from_neo4j()
        
        # Verify update
        content = Content.objects.get(neo4j_id='content.1')
        self.assertEqual(content.content, 'Updated Content')

    @patch('thoughts_app.services.neo4j_service.run_query')
    def test_get_all_thoughts_query_structure(self, mock_run_query):
        """
        Verify that the method calls run_query. 
        We can't easily validate the Cypher string logic without a real DB, 
        but we can ensure usage.
        """
        mock_run_query.return_value = []
        self.service.get_all_thoughts()
        
        args, kwargs = mock_run_query.call_args
        cypher_query = args[0]
        
        # Critical checks for the fix
        self.assertIn("MATCH (parent:TOPIC)-[:HAS_THOUGHT]->(t:THOUGHT)", cypher_query)
        self.assertNotIn("OPTIONAL MATCH (parent)-[:HAS_THOUGHT]->(t)", cypher_query)
