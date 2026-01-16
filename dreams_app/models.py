from django.contrib.auth.models import User
from django.db import models

class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    text = models.TextField()
    analysis_text = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to='dream_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dream by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"