"""
Thoughts service module for Neo4j integration and business logic
"""

from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from neo4j_app.neo4j_service import neo4j_service
from .models import Thought, Content
import logging

logger = logging.getLogger(__name__)


class ThoughtsService:
    """
    Service class for managing thoughts with Neo4j and Django integration
    """
    
    def __init__(self):
        self.neo4j = neo4j_service
    
    def get_all_thoughts(self) -> List[Dict]:
        """
        Get all thoughts from Neo4j
        """
        try:
            query = """
            MATCH (t:THOUGHT)
            OPTIONAL MATCH (parent)-[:HAS_THOUGHT]->(t)
            OPTIONAL MATCH (t)-[:HAS_CONTENT]->(c:CONTENT)
            RETURN t.name as id, 
                   t.alias as title, 
                   t.description as description, 
                   t.en_description as en_description,
                   coalesce(parent.name, '') as parent_id,
                   collect({
                       id: c.name, 
                       content: coalesce(c.en_content, ''),
                       en_title: c.en_title, en_content: c.en_content,
                       es_title: c.es_title, es_content: c.es_content,
                       fr_title: c.fr_title, fr_content: c.fr_content,
                       hi_title: c.hi_title, hi_content: c.hi_content,
                       zh_title: c.zh_title, zh_content: c.zh_content
                   }) as contents
            ORDER BY t.alias
            """
            thoughts = self.neo4j.run_query(query, query_name="get_all_thoughts_full")
            return thoughts
            
        except Exception as e:
            logger.error(f"Error fetching thoughts: {e}")
            return []

    def sync_thoughts_from_neo4j(self) -> Tuple[bool, str, int]:
        """
        Sync thoughts from Neo4j to Django models
        """
        try:
            neo4j_thoughts = self.get_all_thoughts()
            records_processed = 0
            
            for thought_data in neo4j_thoughts:
                try:
                    self._sync_single_thought(thought_data)
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Error syncing thought {thought_data.get('id')}: {e}")
            
            return True, f"Successfully synced {records_processed} thoughts", records_processed
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0

    def _sync_single_thought(self, thought_data: Dict):
        """Sync a single thought to Django model"""
        neo4j_id = thought_data.get('id')
        if not neo4j_id:
            return
        
        thought, created = Thought.objects.update_or_create(
            neo4j_id=neo4j_id,
            defaults={
                'title': thought_data.get('title', ''),
                'description': thought_data.get('description') or thought_data.get('en_description') or '',
                'parent_id': thought_data.get('parent_id'),
                'last_synced': timezone.now(),
            }
        )
        
        # Sync contents
        contents = thought_data.get('contents', [])
        
        # Get existing contents for this thought
        existing_contents = {c.neo4j_id: c for c in Content.objects.filter(thought=thought)}
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
                Content.objects.create(
                    thought=thought,
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
        
        # Delete contents that no longer exist in Neo4j for this thought
        for content_id, content_obj in existing_contents.items():
            if content_id not in processed_ids:
                content_obj.delete()
        
        return thought

# Global service instance
thoughts_service = ThoughtsService()
