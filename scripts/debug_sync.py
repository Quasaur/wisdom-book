import os
import django
import sys

# Add backend to path
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')
django.setup()

from topics_app.services import topics_service
from topics_app.models import Topic
from thoughts_app.services import thoughts_service
from thoughts_app.models import Thought
from quotes_app.services import quotes_service
from quotes_app.models import Quote
from passages_app.services import passages_service
from passages_app.models import Passage
from tags_app.services import TagSyncService
from tags_app.models import TagSource

def debug_sync():
    print("--- Debugging Sync ---")
    
    # 1. Topics Sync
    print("\n--- 1. Syncing Topics ---")
    try:
        success, message, processed = topics_service.sync_topics_from_neo4j(force=True)
        print(f"Topics Sync: Success={success}, Message='{message}', Processed={processed}")
        print(f"Topic DB Count: {Topic.objects.count()}")
    except Exception as e:
        print(f"Error syncing topics: {e}")

    # 2. Thoughts Sync
    print("\n--- 2. Syncing Thoughts ---")
    try:
        success, message, processed = thoughts_service.sync_thoughts_from_neo4j()
        print(f"Thoughts Sync: Success={success}, Message='{message}', Processed={processed}")
        print(f"Thought DB Count: {Thought.objects.count()}")
    except Exception as e:
        print(f"Error syncing thoughts: {e}")

    # 3. Quotes Sync
    print("\n--- 3. Syncing Quotes ---")
    try:
        success, message, processed = quotes_service.sync_quotes_from_neo4j()
        print(f"Quotes Sync: Success={success}, Message='{message}', Processed={processed}")
        print(f"Quote DB Count: {Quote.objects.count()}")
    except Exception as e:
        print(f"Error syncing quotes: {e}")

    # 4. Passages Sync
    print("\n--- 4. Syncing Passages ---")
    try:
        success, message, processed = passages_service.sync_passages_from_neo4j()
        print(f"Passages Sync: Success={success}, Message='{message}', Processed={processed}")
        print(f"Passage DB Count: {Passage.objects.count()}")
    except Exception as e:
        print(f"Error syncing passages: {e}")

    # 5. Tags Sync (Aggregates from SQL)
    print("\n--- 5. Syncing Tags ---")
    try:
        tag_service = TagSyncService()
        processed = tag_service.sync_tags()
        print(f"Tags Sync: Processed={processed}")
        print(f"TagSource DB Count: {TagSource.objects.count()}")
    except Exception as e:
        print(f"Error syncing tags: {e}")

if __name__ == "__main__":
    debug_sync()
