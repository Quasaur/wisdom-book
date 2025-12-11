from django.test import TestCase
from unittest.mock import patch, MagicMock
from .models import Passage, PassageContent
from topics_app.models import Topic
from .services import passages_service

class PassageServiceTests(TestCase):
    def setUp(self):
        # Create a parent topic
        self.topic = Topic.objects.create(
            neo4j_id="topic.GOD",
            title="God",
            slug="god",
            level=1
        )

    @patch('neo4j_app.neo4j_service.Neo4jService.run_query')
    def test_sync_passages_integrity(self, mock_run_query):
        """
        Test that passages are synced correctly with their parent topics.
        User Requirement: Every PASSAGE has a parent TOPIC.
        """
        # Mock Neo4j response with a passage linked to the topic
        mock_run_query.return_value = [{
            'id': 'passage.TEST',
            'title': 'Test Passage',
            'book': 'Test Book',
            'chapter': '1',
            'verse': '1',
            'level': 2,
            'source': 'Test 1:1',
            'tags': ['test'],
            'parent_id': 'topic.GOD', # Links to self.topic
            'contents': []
        }]

        # Run sync
        success, msg, count = passages_service.sync_passages_from_neo4j()

        self.assertTrue(success)
        self.assertEqual(count, 1)

        # Verify integrity
        p = Passage.objects.get(neo4j_id='passage.TEST')
        self.assertEqual(p.title, 'Test Passage')
        self.assertEqual(p.level, 2)
        self.assertIsNotNone(p.parent)
        self.assertEqual(p.parent.neo4j_id, 'topic.GOD')
        self.assertEqual(p.parent, self.topic)

    @patch('neo4j_app.neo4j_service.Neo4jService.run_query')
    def test_sync_orphaned_passage_handling(self, mock_run_query):
        """
        Test behavior when parent topic is missing locally.
        Ideally, we should handle this gracefully (log warning), 
        but data integrity fails if parent is None.
        """
        mock_run_query.return_value = [{
            'id': 'passage.ORPHAN',
            'title': 'Orphan Passage',
            'parent_id': 'topic.MISSING', # Does not exist locally
            'level': 2,
            'contents': []
        }]

        passages_service.sync_passages_from_neo4j()

        p = Passage.objects.get(neo4j_id='passage.ORPHAN')
        # Since topic.MISSING doesn't exist, parent should be None (or we strictly enforce it)
        # Current logic sets it to None and logs a warning.
        self.assertIsNone(p.parent)

    def test_data_integrity_validation(self):
        """
        Test a hypothetical data integrity check.
        Ensures all active passages have parents.
        """
        # Good passage
        Passage.objects.create(
            neo4j_id="p1", title="Good", parent=self.topic, level=2
        )
        # Bad passage (Orphan)
        Passage.objects.create(
            neo4j_id="p2", title="Bad", parent=None, level=2
        )

        # Check: Filter for orphans
        orphans = Passage.objects.filter(parent__isnull=True, is_active=True)
        
        # We expect 1 orphan here in this synthetic test
        self.assertEqual(orphans.count(), 1)
        self.assertEqual(orphans.first().title, "Bad")
