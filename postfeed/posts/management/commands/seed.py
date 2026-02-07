from django.core.management.base import BaseCommand
from posts.factories import (
    UserFactory,
    PostFactory,
    LikeFactory,
    CommentFactory,
    ShareFactory,
)
from analytics.factories import PostAnalyticsFactory
from interactions.factories import InteractionEventFactory


class Command(BaseCommand):
    help = "Seed the database with fake data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        users = UserFactory.create_batch(10)
        posts = PostFactory.create_batch(20)

        LikeFactory.create_batch(30)
        CommentFactory.create_batch(40)
        ShareFactory.create_batch(20)

        for post in posts:
            PostAnalyticsFactory(post=post)

        InteractionEventFactory.create_batch(50)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
