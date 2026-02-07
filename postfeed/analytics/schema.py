import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from posts.models import Post
from .models import PostAnalytics


# GraphQL TYPES

class PostAnalyticsType(DjangoObjectType):
    class Meta:
        model = PostAnalytics
        fields = ("post", "like_count", "comment_count", "share_count", "view_count", "last_interaction_at")


# QUERIES

class Query(graphene.ObjectType):
    analytics_by_post = graphene.Field(PostAnalyticsType, post_id=graphene.Int(required=True))
    all_analytics = graphene.List(PostAnalyticsType)

    def resolve_analytics_by_post(self, info, post_id):
        try:
            return PostAnalytics.objects.get(post_id=post_id)
        except PostAnalytics.DoesNotExist:
            return None

    def resolve_all_analytics(self, info):
        return PostAnalytics.objects.select_related("post").all()


# MUTATIONS

class IncrementView(graphene.Mutation):
    analytics = graphene.Field(PostAnalyticsType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        analytics, _ = PostAnalytics.objects.get_or_create(post=post)
        analytics.view_count += 1
        analytics.save()

        return IncrementView(analytics=analytics)


class UpdateInteractionCounts(graphene.Mutation):
    analytics = graphene.Field(PostAnalyticsType)

    class Arguments:
        post_id = graphene.Int(required=True)
        like_count = graphene.Int()
        comment_count = graphene.Int()
        share_count = graphene.Int()

    def mutate(self, info, post_id, like_count=None, comment_count=None, share_count=None):
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        analytics, _ = PostAnalytics.objects.get_or_create(post=post)

        if like_count is not None:
            analytics.like_count = like_count
        if comment_count is not None:
            analytics.comment_count = comment_count
        if share_count is not None:
            analytics.share_count = share_count

        analytics.save()
        return UpdateInteractionCounts(analytics=analytics)


# MUTATION ROOT

class Mutation(graphene.ObjectType):
    increment_view = IncrementView.Field()
    update_interaction_counts = UpdateInteractionCounts.Field()


# SCHEMA

analytics_schema = graphene.Schema(query=Query, mutation=Mutation)
