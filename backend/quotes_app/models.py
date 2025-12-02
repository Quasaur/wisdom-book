from django.db import models

class Quote(models.Model):
    """
    Quote model for caching and additional metadata
    """
    
    # Core fields that mirror Neo4j
    neo4j_id = models.CharField(max_length=255, unique=True, db_index=True,
                               help_text="Corresponding Neo4j node ID")
    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    book_link = models.CharField(max_length=500, blank=True, help_text="URL to the book")
    
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
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
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


class QuoteContent(models.Model):
    """
    Content model for storing Neo4j CONTENT nodes linked to Quotes
    Linked to Quote via HAS_CONTENT relationship
    """
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='contents')
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
        verbose_name = 'Quote Content'
        verbose_name_plural = 'Quote Contents'
        indexes = [
            models.Index(fields=['neo4j_id']),
        ]

    def __str__(self):
        return f"Content for {self.quote.title}"
