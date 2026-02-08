import factory
from faker import Faker
from analytics.models import PostAnalytics
from posts.factories import PostFactory

fake = Faker()


class PostAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostAnalytics

    post = factory.SubFactory(PostFactory)
    view_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=500))
    like_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=200))
    comment_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))
    share_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))
