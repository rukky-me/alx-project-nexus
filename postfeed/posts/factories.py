import factory
from django.contrib.auth import get_user_model
from faker import Faker
import random

from posts.models import Post, Like, Tag, Comment, Share
from analytics.models import PostAnalytics
from interactions.models import InteractionEvent

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ("name",)

    name = factory.LazyAttribute(lambda _: fake.word())


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    text = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=5))

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            for _ in range(fake.random_int(min=1, max=3)):
                tag = TagFactory()
                self.tags.add(tag)


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.get("user") or UserFactory()
        post = kwargs.get("post") or PostFactory()

        while model_class.objects.filter(user=user, post=post).exists():
            user = random.choice(User.objects.all())
            post = random.choice(Post.objects.all())

        kwargs["user"] = user
        kwargs["post"] = post
        return super()._create(model_class, *args, **kwargs)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    text = factory.LazyAttribute(lambda _: fake.sentence())


class ShareFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Share

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)


class PostAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostAnalytics

    post = factory.SubFactory(PostFactory)
    view_count = factory.Faker("random_int", min=0, max=500)
    like_count = factory.Faker("random_int", min=0, max=100)
    comment_count = factory.Faker("random_int", min=0, max=100)
    share_count = factory.Faker("random_int", min=0, max=50)


class InteractionEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InteractionEvent

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    interaction_type = factory.Iterator(["view", "like", "comment", "share"])
