
from django.core.management.base import BaseCommand
from quotes_app.services import quotes_service

class Command(BaseCommand):
    help = 'Syncs quotes from Neo4j to Django models'

    def handle(self, *args, **options):
        self.stdout.write('Starting quote sync...')
        
        success, message, count = quotes_service.sync_quotes_from_neo4j()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'{message}'))
        else:
            self.stdout.write(self.style.ERROR(f'Sync failed: {message}'))
