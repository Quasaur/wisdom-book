"""
Management command to analyze slow Neo4j queries from the log.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
import tabulate

from neo4j_app.middleware.query_logger import get_slow_query_stats


class Command(BaseCommand):
    help = 'Analyze slow Neo4j queries from the logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-time',
            type=int,
            default=None,
            help='Minimum query time in ms to include'
        )
        parser.add_argument(
            '--group-by',
            type=str,
            default='query_name',
            choices=['query_name', 'request_path', 'user_id'],
            help='Field to group queries by'
        )
        parser.add_argument(
            '--top',
            type=int,
            default=10,
            help='Number of top results to show'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='table',
            choices=['table', 'json'],
            help='Output format'
        )
        parser.add_argument(
            '--log-file',
            type=str,
            default=None,
            help='Path to log file (uses configured value if not specified)'
        )

    def handle(self, *args, **options):
        # Get options
        min_time = options['min_time']
        group_by = options['group_by']
        top_n = options['top']
        output_format = options['output']
        log_file = options['log_file']
        
        # If no log file specified, use the configured one
        if not log_file:
            if hasattr(settings, 'NEO4J_QUERY_LOGGING'):
                log_file = settings.NEO4J_QUERY_LOGGING.get('log_file')
            
            # Make path absolute if needed
            if log_file and not os.path.isabs(log_file):
                log_file = os.path.join(settings.BASE_DIR, log_file)
        
        # Check if log file exists
        if not log_file or not os.path.exists(log_file):
            self.stderr.write(self.style.ERROR(f"Log file not found: {log_file}"))
            return
        
        # Get stats
        stats = get_slow_query_stats(
            log_file=log_file,
            min_time_ms=min_time,
            group_by=group_by,
            top_n=top_n
        )
        
        if not stats:
            self.stdout.write(self.style.WARNING("No slow queries found."))
            return
        
        # Output based on format
        if output_format == 'json':
            self.stdout.write(json.dumps(stats, indent=2))
        else:
            # Prepare table data
            table_data = []
            headers = ["#", "Name", "Count", "Avg (ms)", "Max (ms)", "Min (ms)", "Last Seen"]
            
            for i, stat in enumerate(stats, 1):
                table_data.append([
                    i,
                    stat['name'],
                    stat['count'],
                    f"{stat['avg_time_ms']:.2f}",
                    f"{stat['max_time_ms']:.2f}",
                    f"{stat['min_time_ms']:.2f}",
                    stat['last_occurred'] or 'Unknown'
                ])
            
            # Display table
            self.stdout.write(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Display example of the slowest query
            if stats and 'examples' in stats[0] and stats[0]['examples']:
                slowest = stats[0]['examples'][0]
                self.stdout.write("\nExample of the slowest query:")
                self.stdout.write(f"Query name: {slowest.get('query_name', 'unnamed')}")
                self.stdout.write(f"Time: {slowest.get('elapsed_ms', 0):.2f}ms")
                
                if 'params' in slowest and slowest['params']:
                    self.stdout.write(f"Parameters: {json.dumps(slowest['params'], indent=2)}")
                
                if 'request_path' in slowest:
                    self.stdout.write(f"Endpoint: {slowest.get('request_method', 'GET')} {slowest.get('request_path', '')}")
