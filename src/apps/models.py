from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    """SQL最適化のためのテストモデル"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, default="")
