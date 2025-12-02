from topics_app.models import Topic
from thoughts_app.models import Thought
from quotes_app.models import Quote
from passages_app.models import Passage
from .models import TagSource
import logging

logger = logging.getLogger(__name__)

class TagSyncService:
    def sync_tags(self):
        """
        Aggregates tags from all source apps and populates the TagSource model.
        """
        logger.info("Starting Tag Sync...")
        total_processed = 0
        
        # Sync Topics
        topics = Topic.objects.prefetch_related('topic_tags').all()
        for topic in topics:
            tags = [tt.tag for tt in topic.topic_tags.all()]
            if tags:
                TagSource.objects.update_or_create(
                    source_type='Topic',
                    source_id=str(topic.id),
                    defaults={
                        'name': topic.title,
                        'tags': tags
                    }
                )
                total_processed += 1
        
        # Sync Thoughts
        thoughts = Thought.objects.prefetch_related('thought_tags').all()
        for thought in thoughts:
            tags = [tt.tag for tt in thought.thought_tags.all()]
            if tags:
                TagSource.objects.update_or_create(
                    source_type='Thought',
                    source_id=str(thought.id),
                    defaults={
                        'name': thought.title,
                        'tags': tags
                    }
                )
                total_processed += 1

        # Sync Quotes
        quotes = Quote.objects.prefetch_related('quote_tags').all()
        for quote in quotes:
            tags = [qt.tag for qt in quote.quote_tags.all()]
            if tags:
                TagSource.objects.update_or_create(
                    source_type='Quote',
                    source_id=str(quote.id),
                    defaults={
                        'name': quote.title,
                        'tags': tags
                    }
                )
                total_processed += 1

        # Sync Passages
        passages = Passage.objects.prefetch_related('passage_tags').all()
        for passage in passages:
            tags = [pt.tag for pt in passage.passage_tags.all()]
            if tags:
                TagSource.objects.update_or_create(
                    source_type='Passage',
                    source_id=str(passage.id),
                    defaults={
                        'name': passage.title,
                        'tags': tags
                    }
                )
                total_processed += 1
        
        logger.info(f"Tag Sync Completed. Processed {total_processed} records.")
        return total_processed
