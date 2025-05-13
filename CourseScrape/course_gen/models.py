from django.db import models

# Create your models here.
from django.db import models

class Prompt(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=255, help_text="The main title or subject of the prompt.")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, help_text="The intended difficulty level for the prompt.")
    duration = models.IntegerField(help_text="Estimated course duration in months (or your chosen unit).")
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)     

    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"
