from django.db import models
from posts.models import Post


class PostAnalytics(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="analytics")
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    last_interaction_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Analytics for Post({self.post_id})"
