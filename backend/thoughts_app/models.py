from django.db import models
from django.utils import timezone

class Thought(models.Model):
    """
    Thought model for caching and additional metadata
    """
    
    # Core fields that mirror Neo4j
    neo4j_id = models.CharField(max_length=255, unique=True, db_index=True,
                               help_text="Corresponding Neo4j node ID")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    parent_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID of the parent topic/thought")
    
    # Additional Django-specific fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(auto_now=True,
                                      help_text="Last sync with Neo4j")
    
    # SEO and metadata
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Thought'
        verbose_name_plural = 'Thoughts'
        indexes = [
            models.Index(fields=['neo4j_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Content(models.Model):
    """
    Content model for storing Neo4j CONTENT nodes
    Linked to Thought via HAS_CONTENT relationship
    """
    thought = models.ForeignKey(Thought, on_delete=models.CASCADE, related_name='contents')
    neo4j_id = models.CharField(max_length=255, unique=True, db_index=True)
    content = models.TextField(blank=True)  # Keeping as fallback/generic
    
    # Language specific fields
    en_title = models.CharField(max_length=255, blank=True)
    en_content = models.TextField(blank=True)
    
    es_title = models.CharField(max_length=255, blank=True)
    es_content = models.TextField(blank=True)
    
    fr_title = models.CharField(max_length=255, blank=True)
    fr_content = models.TextField(blank=True)
    
    hi_title = models.CharField(max_length=255, blank=True)
    hi_content = models.TextField(blank=True)
    
    zh_title = models.CharField(max_length=255, blank=True)
    zh_content = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thought Content'
        verbose_name_plural = 'Thought Contents'
        indexes = [
            models.Index(fields=['neo4j_id']),
        ]

    def __str__(self):
        return f"Content for {self.thought.title}"


class ThoughtTag(models.Model):
    """Tags for thoughts (separate model for better performance)"""
    
    thought = models.ForeignKey(Thought, on_delete=models.CASCADE, related_name='thought_tags')
    tag = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['thought', 'tag']
        indexes = [
            models.Index(fields=['tag']),
        ]
    
    def __str__(self):
        return f"{self.thought.title} - {self.tag}"
