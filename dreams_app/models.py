from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Dream(models.Model):
    user =models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dreams'
    )

    text = models.TextField()
    analysis_text = models.TextField(blank=True)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dream by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"