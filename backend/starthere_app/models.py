from django.db import models

class StartHerePage(models.Model):
    """
    Singleton model for the Start Here page content.
    """
    title = models.CharField(max_length=255, default="Welcome to the Book of Wisdom!")
    subtitle = models.CharField(max_length=255, blank=True, default="Formerly 'The Book of Tweets: Proverbs for the Modern Age'")
    hero_image_url = models.CharField(max_length=255, default="/assets/images/hero_image.jpg", help_text="Path to the hero image")
    content = models.TextField(help_text="Main content of the page. Supports HTML.")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Start Here Page Content"
        verbose_name_plural = "Start Here Page Content"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Singleton pattern: ensure only one instance exists
        if not self.pk and StartHerePage.objects.exists():
            # If trying to create a new one, update the existing one instead
            existing = StartHerePage.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

