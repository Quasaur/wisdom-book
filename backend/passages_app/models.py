from django.db import models

class Passage(models.Model):
    """
    Passage model for caching and additional metadata
    """
    
    # Core fields that mirror Neo4j
    neo4j_id = models.CharField(max_length=255, unique=True, db_index=True,
                               help_text="Corresponding Neo4j node ID")
    title = models.CharField(max_length=255, db_index=True)
    book = models.CharField(max_length=255, blank=True)
    chapter = models.CharField(max_length=255, blank=True)
    verse = models.CharField(max_length=255, blank=True)
    
    # Additional Django-specific fields
    is_active = models.BooleanField(default=True)
    level = models.IntegerField(default=0)
    parent = models.ForeignKey('topics_app.Topic', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='passages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(auto_now=True,
                                      help_text="Last sync with Neo4j")
    
    # SEO and metadata
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    source = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['title']
        verbose_name = 'Passage'
        verbose_name_plural = 'Passages'
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


class PassageTag(models.Model):
    """Tags for passages"""
    
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='passage_tags')
    tag = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['passage', 'tag']
        indexes = [
            models.Index(fields=['tag']),
        ]
    
    def __str__(self):
        return f"{self.passage.title} - {self.tag}"


class PassageContent(models.Model):
    """
    Content model for storing Neo4j CONTENT nodes linked to Passages
    Linked to Passage via HAS_CONTENT relationship
    """
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='contents')
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
        verbose_name = 'Passage Content'
        verbose_name_plural = 'Passage Contents'
        indexes = [
            models.Index(fields=['neo4j_id']),
        ]

    def __str__(self):
        return f"Content for {self.passage.title}"
