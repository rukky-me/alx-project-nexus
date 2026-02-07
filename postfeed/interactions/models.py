from django.db import models
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


class InteractionEvent(models.Model):
    INTERACTION_TYPES = (
        ("like", "Like"),
        ("comment", "Comment"),
        ("share", "Share"),
        ("view", "View"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interaction_events")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="interaction_events")
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["user"]),
            models.Index(fields=["interaction_type"]),
        ]

    def __str__(self):
        return f"{self.interaction_type} by {self.user_id} on Post({self.post_id})"
