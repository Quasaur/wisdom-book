from django.core.management.base import BaseCommand
from thoughts_app.services import thoughts_service

class Command(BaseCommand):
    help = 'Syncs thoughts from Neo4j to Postgres, removing stale entries'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting thought sync...')
        success, msg, count = thoughts_service.sync_thoughts_from_neo4j()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'{msg}'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed: {msg}'))
