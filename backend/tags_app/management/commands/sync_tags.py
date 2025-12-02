from django.core.management.base import BaseCommand
from tags_app.services import TagSyncService

class Command(BaseCommand):
    help = 'Aggregates tags from Topics, Thoughts, Quotes, and Passages into the Tags App'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting tag sync...')
        service = TagSyncService()
        count = service.sync_tags()
        self.stdout.write(self.style.SUCCESS(f'Successfully synced {count} tag sources'))
