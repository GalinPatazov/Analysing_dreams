from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Dream(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)        # Dream title
    text = models.TextField()                       # Full dream text
    analysis_text = models.TextField(blank=True, null=True)  # AI analysis
    image = models.URLField(
        blank=True,
        null=True,
        default="/static/dreams_app/images/placeholder.png"
    )  # Placeholder if AI image fails
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dream by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"