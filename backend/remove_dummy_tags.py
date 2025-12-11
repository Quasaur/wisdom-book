from tags_app.models import TagSource

def remove_dummy_tags():
    print("Starting cleanup of 'dummy' tags...")
    count = 0
    records = TagSource.objects.all()
    
    for source in records:
        original_tags = list(source.tags)
        # Filter out 'dummy' (case-insensitive)
        new_tags = [t for t in original_tags if t.lower() != 'dummy']
        
        if len(new_tags) != len(original_tags):
            source.tags = new_tags
            source.save()
            count += 1
            print(f"Removed 'dummy' from {source.source_type}: {source.name}")

    print(f"Cleanup complete. Modified {count} records.")

remove_dummy_tags()
