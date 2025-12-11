from django.test import TestCase
from topics_app.models import Topic, TopicTag
from thoughts_app.models import Thought, ThoughtTag
from tags_app.models import TagSource
from tags_app.services import TagSyncService

class TagSyncServiceTests(TestCase):
    def setUp(self):
        self.service = TagSyncService()

    def test_sync_creates_tags_from_topic(self):
        """Test that sync creates TagSource records from Topics."""
        topic = Topic.objects.create(title="Test Topic")
        TopicTag.objects.create(topic=topic, tag="TestTag1")
        TopicTag.objects.create(topic=topic, tag="TestTag2")

        self.service.sync_tags()

        tag_source = TagSource.objects.get(source_type='Topic', source_id=str(topic.id))
        self.assertEqual(tag_source.name, "Test Topic")
        self.assertIn("TestTag1", tag_source.tags)
        self.assertIn("TestTag2", tag_source.tags)

    def test_sync_removes_orphans(self):
        """Test that sync removes TagSource records when the source is deleted."""
        # Create and sync
        topic = Topic.objects.create(title="Temp Topic")
        TopicTag.objects.create(topic=topic, tag="TempTag")
        self.service.sync_tags()
        
        # Verify existence
        self.assertTrue(TagSource.objects.filter(source_type='Topic', source_id=str(topic.id)).exists())

        # Delete source and sync again
        topic.delete()
        self.service.sync_tags()

        # Verify removal
        self.assertFalse(TagSource.objects.filter(source_type='Topic', source_id=str(topic.id)).exists())

    def test_sync_handles_multiple_sources(self):
        """Test that sync handles multiple source types and selective deletion."""
        topic = Topic.objects.create(title="Topic 1")
        TopicTag.objects.create(topic=topic, tag="Tag1")
        
        thought = Thought.objects.create(title="Thought 1")
        ThoughtTag.objects.create(thought=thought, tag="Tag2")

        self.service.sync_tags()
        
        self.assertEqual(TagSource.objects.count(), 2)

        # Delete only the Topic
        topic.delete()
        self.service.sync_tags()

        self.assertEqual(TagSource.objects.count(), 1)
        self.assertTrue(TagSource.objects.filter(source_type='Thought', source_id=str(thought.id)).exists())
