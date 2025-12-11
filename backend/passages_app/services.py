"""
Passages service module for Neo4j integration and business logic
"""

from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from neo4j_app.neo4j_service import neo4j_service
from .models import Passage, PassageContent
import logging

logger = logging.getLogger(__name__)


class PassagesService:
    """
    Service class for managing passages with Neo4j and Django integration
    """
    
    def __init__(self):
        self.neo4j = neo4j_service
    
    def get_all_passages(self) -> List[Dict]:
        """
        Get all passages from Neo4j
        """
        try:
            query = """
            MATCH (p:PASSAGE)
            OPTIONAL MATCH (t:TOPIC)-[:HAS_PASSAGE]->(p)
            OPTIONAL MATCH (p)-[:HAS_CONTENT]->(c:CONTENT)
            RETURN p.name as id, 
                   p.alias as title, 
                   p.book as book,
                   p.chapter as chapter,
                   p.verse as verse,
                   p.level as level,
                   p.source as source,
                   p.tags as tags,
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
            ORDER BY p.alias
            """
            passages = self.neo4j.run_query(query, query_name="get_all_passages_full")
            return passages
            
        except Exception as e:
            logger.error(f"Error fetching passages: {e}")
            return []

    def sync_passages_from_neo4j(self) -> Tuple[bool, str, int]:
        """
        Sync passages from Neo4j to Django models
        """
        try:
            neo4j_passages = self.get_all_passages()
            records_processed = 0
            
            for passage_data in neo4j_passages:
                try:
                    self._sync_single_passage(passage_data)
                    records_processed += 1
                except Exception as e:
                    logger.error(f"Error syncing passage {passage_data.get('id')}: {e}")
            
            return True, f"Successfully synced {records_processed} passages", records_processed
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0

    def _sync_single_passage(self, passage_data: Dict):
        """Sync a single passage to Django model"""
        neo4j_id = passage_data.get('id')
        if not neo4j_id:
            return
        
        # Resolve parent topic if available
        parent_id = passage_data.get('parent_id')
        parent_topic = None
        if parent_id:
            from topics_app.models import Topic
            try:
                parent_topic = Topic.objects.get(neo4j_id=parent_id)
            except Topic.DoesNotExist:
                logger.warning(f"Parent topic {parent_id} not found for passage {neo4j_id}")
        
        passage, created = Passage.objects.update_or_create(
            neo4j_id=neo4j_id,
            defaults={
                'title': passage_data.get('title') or '',
                'book': passage_data.get('book') or '',
                'chapter': passage_data.get('chapter') or '',
                'verse': passage_data.get('verse') or '',
                'source': passage_data.get('source') or '',
                'level': passage_data.get('level') or 0,
                'parent': parent_topic,
                'last_synced': timezone.now(),
            }
        )
        
        # Sync contents
        contents = passage_data.get('contents', [])
        
        # Get existing contents for this passage
        existing_contents = {c.neo4j_id: c for c in PassageContent.objects.filter(passage=passage)}
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
                PassageContent.objects.create(
                    passage=passage,
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
        
        # Delete contents that no longer exist in Neo4j for this passage
        for content_id, content_obj in existing_contents.items():
            if content_id not in processed_ids:
                content_obj.delete()
        
        # Sync tags
        tags = passage_data.get('tags', [])
        from .models import PassageTag
        
        # Get existing tags
        existing_tags = {t.tag: t for t in PassageTag.objects.filter(passage=passage)}
        current_tags = set(tags)
        
        # Create new tags
        for tag_name in current_tags:
            if tag_name and tag_name not in existing_tags:
                PassageTag.objects.create(passage=passage, tag=tag_name)
        
        # Delete removed tags
        for tag_name, tag_obj in existing_tags.items():
            if tag_name not in current_tags:
                tag_obj.delete()
        
        return passage

# Global service instance
passages_service = PassagesService()
