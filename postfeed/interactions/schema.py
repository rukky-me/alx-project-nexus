import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from posts.models import Post
from .models import InteractionEvent

User = get_user_model()

# GraphQL TYPES

class InteractionEventType(DjangoObjectType):
    class Meta:
        model = InteractionEvent
        fields = ("user", "post", "interaction_type", "created_at")


# QUERIES

class Query(graphene.ObjectType):
    interactions_by_post = graphene.List(InteractionEventType, post_id=graphene.Int(required=True))
    interactions_by_user = graphene.List(InteractionEventType, user_id=graphene.Int(required=True))
    all_interactions = graphene.List(InteractionEventType)

    def resolve_interactions_by_post(self, info, post_id):
        return InteractionEvent.objects.filter(post_id=post_id).select_related("user", "post")

    def resolve_interactions_by_user(self, info, user_id):
        return InteractionEvent.objects.filter(user_id=user_id).select_related("user", "post")

    def resolve_all_interactions(self, info):
        return InteractionEvent.objects.select_related("user", "post").all()

# MUTATIONS

class CreateInteraction(graphene.Mutation):
    interaction = graphene.Field(InteractionEventType)

    class Arguments:
        post_id = graphene.Int(required=True)
        interaction_type = graphene.String(required=True)  # like, comment, share, view

    def mutate(self, info, post_id, interaction_type):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        if interaction_type not in ["like", "comment", "share", "view"]:
            raise GraphQLError("Invalid interaction type")

        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        interaction = InteractionEvent.objects.create(
            user=user,
            post=post,
            interaction_type=interaction_type,
        )

        return CreateInteraction(interaction=interaction)


# MUTATION ROOT

class Mutation(graphene.ObjectType):
    create_interaction = CreateInteraction.Field()

# SCHEMA

interactions_schema = graphene.Schema(query=Query, mutation=Mutation)
