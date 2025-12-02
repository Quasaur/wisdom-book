from django.db import models

class TagSource(models.Model):
    """
    Model to store aggregated tags from various sources (Topics, Thoughts, Quotes, Passages).
    This model is populated by syncing data from other apps, not directly from Neo4j.
    """
    SOURCE_TYPES = [
        ('Topic', 'Topic'),
        ('Thought', 'Thought'),
        ('Quote', 'Quote'),
        ('Passage', 'Passage'),
    ]

    name = models.CharField(max_length=255, db_index=True, help_text="Name or Title of the source node")
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, db_index=True)
    source_id = models.CharField(max_length=255, db_index=True, help_text="ID of the source node (e.g., Neo4j ID or PK)")
    tags = models.JSONField(default=list, blank=True, help_text="List of tags associated with the source")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag Source'
        verbose_name_plural = 'Tag Sources'
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['name']),
        ]
        unique_together = ['source_type', 'source_id']

    def __str__(self):
        return f"{self.name} ({self.source_type})"
