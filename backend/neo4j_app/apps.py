from django.apps import AppConfig
from django.conf import settings


class Neo4jAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'neo4j_app'

    def ready(self):
        # Initialize query logging when app is ready
        from .middleware.query_logger import configure_query_logging
        
        # Get configuration from settings
        config = getattr(settings, 'NEO4J_QUERY_LOGGING', {})
        
        # Configure query logging
        configure_query_logging(config)
        
        # Ensure logs directory exists
        import os
        log_file = config.get('log_file')
        if log_file and not os.path.isabs(log_file):
            log_dir = os.path.join(settings.BASE_DIR, os.path.dirname(log_file))
            os.makedirs(log_dir, exist_ok=True)
