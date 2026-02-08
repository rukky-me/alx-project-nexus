import factory
from interactions.models import InteractionEvent
from posts.factories import UserFactory, PostFactory


class InteractionEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InteractionEvent

    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    interaction_type = factory.Iterator(["view", "like", "comment", "share"])
