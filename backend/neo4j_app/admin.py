import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict

from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.html import format_html
from django.template.response import TemplateResponse

from .middleware.query_logger import get_slow_query_stats
from .models import VirtualLogEntry


class Neo4jAdmin(admin.ModelAdmin):
    # Virtual model admin - doesn't use a real model
    model = None
    
    # Admin customization
    change_list_template = 'admin/neo4j_app/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='neo4j_dashboard'),
            path('logs/', self.admin_site.admin_view(self.logs_view), name='neo4j_logs'),
            path('query/<str:query_name>/', self.admin_site.admin_view(self.query_detail_view), name='neo4j_query_detail'),
            path('api/stats/', self.admin_site.admin_view(self.api_stats), name='neo4j_api_stats'),
        ]
        return custom_urls + urls
    
    def get_log_file(self):
        """Get the Neo4j query log file path"""
        log_file = 'neo4j_slow_queries.log'
        
        # Check settings if available
        if hasattr(settings, 'NEO4J_QUERY_LOGGING'):
            log_file = settings.NEO4J_QUERY_LOGGING.get('log_file', log_file)
        
        # Make path absolute if needed
        if log_file and not os.path.isabs(log_file):
            log_file = os.path.join(settings.BASE_DIR, log_file)
            
        return log_file
    
    def parse_log_entries(self, max_entries=1000, filter_level=None, query_name=None, path=None, error_only=False):
        """Parse the log file and return log entries"""
        log_file = self.get_log_file()
        if not os.path.exists(log_file):
            return []
            
        entries = []
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    # Basic log format parsing
                    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(\w+)\] (.*)', line)
                    if not match:
                        continue
                        
                    timestamp_str, level, message = match.groups()
                    
                    # Filter by level if specified
                    if filter_level and level != filter_level:
                        continue
                        
                    # Extract context if available
                    context = {}
                    if '"context":' in line:
                        try:
                            context_str = line.split('"context":')[1].strip()
                            if context_str.endswith('}'):
                                context_str = context_str[:-1]
                            context = json.loads(context_str)
                        except Exception:
                            pass
                    
                    # Parse query details
                    query_name_match = re.search(r'Neo4j Query: (\w+)', message)
                    extracted_query_name = query_name_match.group(1) if query_name_match else 'unnamed'
                    
                    # Filter by query name if specified
                    if query_name and extracted_query_name != query_name:
                        continue
                        
                    # Extract duration
                    duration_match = re.search(r'([\d.]+)ms', message)
                    duration_ms = float(duration_match.group(1)) if duration_match else None
                    
                    # Extract query text if available
                    query_text = None
                    if 'Full slow query:' in message:
                        query_text = message.split('Full slow query:')[1].strip()
                    
                    # Extract error
                    error = None
                    if 'Error:' in message or level == 'ERROR':
                        error = message
                        
                    # Extract path if available
                    request_path = context.get('request_path')
                    
                    # Filter by path if specified
                    if path and request_path != path:
                        continue
                        
                    # Filter by error only if specified
                    if error_only and not error and level != 'ERROR':
                        continue
                    
                    # Create log entry
                    entry = VirtualLogEntry(
                        timestamp=timestamp_str,
                        level=level,
                        message=message,
                        query_name=extracted_query_name,
                        duration_ms=duration_ms,
                        is_slow='(SLOW)' in message,
                        query_text=query_text,
                        error=error,
                        context=context,
                        path=request_path
                    )
                    
                    entries.append(entry)
                    
                    # Limit number of entries to prevent memory issues
                    if len(entries) >= max_entries:
                        break
                        
            # Sort by timestamp (newest first)
            entries.reverse()
            
            return entries
            
        except Exception as e:
            return [VirtualLogEntry(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
                level='ERROR',
                message=f"Error parsing log file: {e}",
                error=str(e)
            )]
    
    def dashboard_view(self, request):
        """Main Neo4j admin dashboard view"""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Neo4j Dashboard',
        }
        
        # Get query stats
        try:
            query_stats = get_slow_query_stats(top_n=10)
            context['query_stats'] = query_stats
        except Exception as e:
            context['query_stats_error'] = str(e)
        
        # Get recent errors
        error_entries = self.parse_log_entries(max_entries=5, error_only=True)
        context['recent_errors'] = error_entries
        
        # Get overall stats
        all_entries = self.parse_log_entries(max_entries=1000)
        
        # Count by level
        level_counts = defaultdict(int)
        for entry in all_entries:
            level_counts[entry.level] += 1
            
        context['level_counts'] = dict(level_counts)
        
        # Count by path
        path_counts = defaultdict(int)
        for entry in all_entries:
            if entry.path:
                path_counts[entry.path] += 1
                
        context['path_counts'] = dict(path_counts)
        
        return TemplateResponse(request, self.change_list_template, context)
    
    def logs_view(self, request):
        """View showing all log entries with filtering"""
        filter_level = request.GET.get('level')
        query_name = request.GET.get('query_name')
        path = request.GET.get('path')
        error_only = request.GET.get('error_only') == '1'
        
        entries = self.parse_log_entries(
            filter_level=filter_level,
            query_name=query_name,
            path=path,
            error_only=error_only
        )
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Neo4j Query Logs',
            'entries': entries,
            'filter_level': filter_level,
            'query_name': query_name,
            'path': path,
            'error_only': error_only,
        }
        
        return TemplateResponse(request, 'admin/neo4j_app/logs.html', context)
    
    def query_detail_view(self, request, query_name):
        """View showing details of a specific query type"""
        entries = self.parse_log_entries(query_name=query_name)
        
        # Get stats for this query
        stats = get_slow_query_stats(group_by="query_name")
        query_stats = next((s for s in stats if s['name'] == query_name), None)
        
        # Create example with solution if there are errors
        error_entries = [e for e in entries if e.has_error]
        solution = error_entries[0].solution if error_entries else None
        
        context = {
            **self.admin_site.each_context(request),
            'title': f'Query Details: {query_name}',
            'query_name': query_name,
            'entries': entries,
            'stats': query_stats,
            'solution': solution,
            'error_entries': error_entries,
        }
        
        return TemplateResponse(request, 'admin/neo4j_app/query_detail.html', context)
    
    def api_stats(self, request):
        """API endpoint for query stats used in charts"""
        days = int(request.GET.get('days', 7))
        query_name = request.GET.get('query_name')
        
        # Get log entries for the time period
        entries = self.parse_log_entries(max_entries=10000)
        if query_name:
            entries = [e for e in entries if e.query_name == query_name]
        
        # Filter by date range
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        # Format: 2023-05-14 15:30:12,123
        date_format = '%Y-%m-%d %H:%M:%S,%f'
        filtered_entries = []
        
        for entry in entries:
            try:
                entry_date = datetime.strptime(entry.timestamp, date_format)
                if entry_date >= start_date:
                    filtered_entries.append(entry)
            except ValueError:
                # Skip entries with invalid timestamps
                continue
                
        # Group by day for chart
        daily_stats = defaultdict(lambda: {'count': 0, 'errors': 0, 'total_ms': 0, 'max_ms': 0})
        
        for entry in filtered_entries:
            try:
                entry_date = datetime.strptime(entry.timestamp, date_format)
                day_key = entry_date.strftime('%Y-%m-%d')
                
                daily_stats[day_key]['count'] += 1
                if entry.has_error:
                    daily_stats[day_key]['errors'] += 1
                    
                if entry.duration_ms:
                    daily_stats[day_key]['total_ms'] += entry.duration_ms
                    daily_stats[day_key]['max_ms'] = max(
                        daily_stats[day_key]['max_ms'], entry.duration_ms
                    )
            except ValueError:
                continue
                
        # Calculate averages
        for day, stats in daily_stats.items():
            if stats['count'] > 0:
                stats['avg_ms'] = stats['total_ms'] / stats['count']
            else:
                stats['avg_ms'] = 0
                
        # Sort by date
        sorted_stats = [
            {'date': day, **stats}
            for day, stats in sorted(daily_stats.items())
        ]
        
        return JsonResponse({'data': sorted_stats})

    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False


# Register with custom name
admin.site.register([object], Neo4jAdmin)
admin.site._registry[object]._meta.app_label = 'neo4j_app'
admin.site._registry[object]._meta.model_name = 'neo4j_log'
admin.site._registry[object]._meta.verbose_name = 'Neo4j Log'
admin.site._registry[object]._meta.verbose_name_plural = 'Neo4j Logs'
