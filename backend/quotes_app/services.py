"""
Quotes service module for Neo4j integration and business logic
"""

from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from neo4j_app.neo4j_service import neo4j_service
from .models import Quote, QuoteContent
import logging

logger = logging.getLogger(__name__)


class QuotesService:
    """
    Service class for managing quotes with Neo4j and Django integration
    """
    
    def __init__(self):
        self.neo4j = neo4j_service
    
    def get_all_quotes(self) -> List[Dict]:
        """
        Get all quotes from Neo4j
        """
        try:
            query = """
            MATCH (q:QUOTE)
            OPTIONAL MATCH (t:TOPIC)-[:HAS_QUOTE]->(q)
            OPTIONAL MATCH (q)-[:HAS_CONTENT]->(c:CONTENT)
            RETURN q.name as id, 
                   q.alias as title, 
                   q.author as author,
                   q.level as level,
                   q.source as source,
                   q.booklink as book_link,
                   q.tags as tags,
                   t.name as parent_id,
                   collect({
                       id: c.name, 
                       content: coalesce(c.en_content, ''),
                       en_title: c.en_title, en_content: c.en_content,
                       es_title: c.es_title, es_content: c.es_content,
                       fr_title: c.fr_title, fr_content: c.fr_content,
                       hi_title: c.hi_title, hi_content: c.hi_content,
                       zh_title: c.zh_title, zh_content: c.zh_content
                   }) as contents
            ORDER BY q.alias
            """
            quotes = self.neo4j.run_query(query, query_name="get_all_quotes_full")
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return []

    def sync_quotes_from_neo4j(self) -> Tuple[bool, str, int]:
        """
        Sync quotes from Neo4j to Django models
        """
        try:
            neo4j_quotes = self.get_all_quotes()
            records_processed = 0
            
            for quote_data in neo4j_quotes:
                try:
                    self._sync_single_quote(quote_data)
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Error syncing quote {quote_data.get('id')}: {e}")
            
            return True, f"Successfully synced {records_processed} quotes", records_processed
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0

    def _sync_single_quote(self, quote_data: Dict):
        """Sync a single quote to Django model"""
        neo4j_id = quote_data.get('id')
        if not neo4j_id:
            return

        # Resolve parent topic if available
        parent_id = quote_data.get('parent_id')
        parent_topic = None
        if parent_id:
            from topics_app.models import Topic
            try:
                parent_topic = Topic.objects.get(neo4j_id=parent_id)
            except Topic.DoesNotExist:
                logger.warning(f"Parent topic {parent_id} not found for quote {neo4j_id}")
        
        quote, created = Quote.objects.update_or_create(
            neo4j_id=neo4j_id,
            defaults={
                'title': quote_data.get('title') or '',
                'author': quote_data.get('author') or '',
                'level': quote_data.get('level') or 0,
                'parent': parent_topic,
                'source': quote_data.get('source') or '',
                'book_link': quote_data.get('book_link') or '',
                'last_synced': timezone.now(),
            }
        )
        
        # Sync contents
        contents = quote_data.get('contents', [])
        
        # Get existing contents for this quote
        existing_contents = {c.neo4j_id: c for c in QuoteContent.objects.filter(quote=quote)}
        processed_ids = set()
        
        for content_data in contents:
            content_id = content_data.get('id')
            content_text = content_data.get('content', '')
            
            if not content_id:
                continue
                
            processed_ids.add(content_id)
            
            if content_id in existing_contents:
                # Update existing
                content_obj = existing_contents[content_id]
                content_obj.content = content_text
                content_obj.en_title = content_data.get('en_title') or ''
                content_obj.en_content = content_data.get('en_content') or ''
                content_obj.es_title = content_data.get('es_title') or ''
                content_obj.es_content = content_data.get('es_content') or ''
                content_obj.fr_title = content_data.get('fr_title') or ''
                content_obj.fr_content = content_data.get('fr_content') or ''
                content_obj.hi_title = content_data.get('hi_title') or ''
                content_obj.hi_content = content_data.get('hi_content') or ''
                content_obj.zh_title = content_data.get('zh_title') or ''
                content_obj.zh_content = content_data.get('zh_content') or ''
                content_obj.save()
            else:
                # Create new
                QuoteContent.objects.create(
                    quote=quote,
                    neo4j_id=content_id,
                    content=content_text,
                    en_title=content_data.get('en_title') or '',
                    en_content=content_data.get('en_content') or '',
                    es_title=content_data.get('es_title') or '',
                    es_content=content_data.get('es_content') or '',
                    fr_title=content_data.get('fr_title') or '',
                    fr_content=content_data.get('fr_content') or '',
                    hi_title=content_data.get('hi_title') or '',
                    hi_content=content_data.get('hi_content') or '',
                    zh_title=content_data.get('zh_title') or '',
                    zh_content=content_data.get('zh_content') or ''
                )
        
        # Delete contents that no longer exist in Neo4j for this quote
        for content_id, content_obj in existing_contents.items():
            if content_id not in processed_ids:
                content_obj.delete()
        
        # Sync tags
        tags = quote_data.get('tags', [])
        from .models import QuoteTag
        
        # Get existing tags
        existing_tags = {t.tag: t for t in QuoteTag.objects.filter(quote=quote)}
        current_tags = set(tags)
        
        # Create new tags
        for tag_name in current_tags:
            if tag_name and tag_name not in existing_tags:
                QuoteTag.objects.create(quote=quote, tag=tag_name)
        
        # Delete removed tags
        for tag_name, tag_obj in existing_tags.items():
            if tag_name not in current_tags:
                tag_obj.delete()
        
        return quote

# Global service instance
quotes_service = QuotesService()
