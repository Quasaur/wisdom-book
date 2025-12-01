from django.core.management.base import BaseCommand
from topics_app.services import topics_service

class Command(BaseCommand):
    help = 'Syncs topics from Neo4j to Django models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force full sync even if recent sync exists',
        )

    def handle(self, *args, **options):
        force = options['force']
        self.stdout.write('Starting topic sync...')
        
        success, message, count = topics_service.sync_topics_from_neo4j(force=force)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'{message}'))
        else:
            self.stdout.write(self.style.ERROR(f'Sync failed: {message}'))
