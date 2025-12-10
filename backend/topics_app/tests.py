from django.test import TestCase
from .models import Topic

class TopicModelTests(TestCase):
    def test_create_topic(self):
        """Test basic topic creation"""
        topic = Topic.objects.create(
            neo4j_id="topic_1",
            title="Test Topic",
            level=1,
            slug="test-topic"
        )
        self.assertEqual(topic.title, "Test Topic")
        self.assertEqual(str(topic), "Test Topic (L1)")
