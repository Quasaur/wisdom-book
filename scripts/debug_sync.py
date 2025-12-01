import os
import django
import sys

# Add backend to path
sys.path.append('/Users/quasaur/Developer/wisdom-book/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')
django.setup()

from topics_app.services import topics_service
from topics_app.models import Topic

def debug_sync():
    print("--- Debugging Sync ---")
    
    # 1. Check Neo4j Data
    print("\n1. Fetching data from Neo4j...")
    try:
        topics = topics_service.get_all_topics(use_cache=False, sync_if_missing=False)
        print(f"Fetched {len(topics)} topics from Neo4j.")
        if topics:
            print("First topic sample:")
            print(topics[0])
            if 'id' not in topics[0]:
                print("CRITICAL: 'id' field missing in topic data!")
            else:
                print(f"Topic ID: {topics[0].get('id')}")
    except Exception as e:
        print(f"Error fetching topics: {e}")
        return

    # 2. Check Database before sync
    count_before = Topic.objects.count()
    print(f"\n2. Topic count before sync: {count_before}")

    # 3. Run Sync
    print("\n3. Running Sync...")
    success, message, processed = topics_service.sync_topics_from_neo4j(force=True)
    print(f"Sync Result: Success={success}, Message='{message}', Processed={processed}")

    # 4. Check Database after sync
    count_after = Topic.objects.count()
    print(f"\n4. Topic count after sync: {count_after}")
    
    if count_after == 0 and processed > 0:
        print("\nCRITICAL: Processed records but DB count is 0. _sync_single_topic is likely failing silently.")

if __name__ == "__main__":
    debug_sync()
