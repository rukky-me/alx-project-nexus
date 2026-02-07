import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql import GraphQLError

from .models import Post, Like, Tag, Comment, Share

User = get_user_model()

# GraphQL TYPES
#This defines the fields(TYPES) that can be queried alongside the objects in the Users that are exposed to graphql from django
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ("id", "author", "post", "text", "created_at")


class PostType(DjangoObjectType):
    like_count = graphene.Int()
    comment_count = graphene.Int()
    share_count = graphene.Int()
    comments = graphene.List(CommentType)

    class Meta:
        model = Post
        fields = ("id", "author", "text", "tags", "created_at", "updated_at")

#This resolves how GraphQL calculates the field
#Returns number of likes for a post.
    def resolve_like_count(self, info):
        return self.likes.count()

#This counts only non deleted comments
    def resolve_comment_count(self, info):
        return self.comments.filter(is_deleted=False).count()

    def resolve_share_count(self, info):
        return self.shares.count()

    def resolve_comments(self, info):
        return self.comments.filter(is_deleted=False).select_related("author")


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")


class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = ("id", "user", "post", "created_at")


# QUERIES

class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))
    posts_by_user = graphene.List(PostType, user_id=graphene.Int(required=True))
    all_tags = graphene.List(TagType)

    def resolve_all_posts(self, info):
        return Post.objects.filter(is_deleted=False).select_related("author").prefetch_related("tags", "likes", "comments", "shares").order_by("-created_at")

    def resolve_post_by_id(self, info, id):
        try:
            return Post.objects.filter(is_deleted=False).get(id=id)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

    def resolve_posts_by_user(self, info, user_id):
        return Post.objects.filter(is_deleted=False, author_id=user_id).select_related("author").prefetch_related("tags", "likes", "comments", "shares")

    def resolve_all_tags(self, info):
        return Tag.objects.all()


# MUTATIONS
#This basically performs the CRUD operations
class CreatePost(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        text = graphene.String(required=True)
        tag_names = graphene.List(graphene.String)

    def mutate(self, info, text, tag_names=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        post = Post.objects.create(author=user, text=text)

        if tag_names:
            tags = [Tag.objects.get_or_create(name=name.lower())[0] for name in tag_names]
            post.tags.set(tags)

        return CreatePost(post=post)


class DeletePost(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        try:
            post = Post.objects.get(id=post_id, author=user)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found or not authorized")

        post.is_deleted = True
        post.save()
        return DeletePost(success=True)


class CreateComment(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        post_id = graphene.Int(required=True)
        text = graphene.String(required=True)

    def mutate(self, info, post_id, text):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        comment = Comment.objects.create(author=user, post=post, text=text)
        return CreateComment(comment=comment)


class DeleteComment(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        comment_id = graphene.Int(required=True)

    def mutate(self, info, comment_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        try:
            comment = Comment.objects.get(id=comment_id, author=user)
        except Comment.DoesNotExist:
            raise GraphQLError("Comment not found or not authorized")

        comment.is_deleted = True
        comment.save()
        return DeleteComment(success=True)


class LikePost(graphene.Mutation):
    like = graphene.Field(LikeType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            raise GraphQLError("You have already liked this post")

        return LikePost(like=like)


class UnlikePost(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        deleted, _ = Like.objects.filter(user=user, post_id=post_id).delete()
        if deleted == 0:
            raise GraphQLError("Like does not exist")

        return UnlikePost(success=True)


class SharePost(graphene.Mutation):
    share = graphene.Field(ShareType)

    class Arguments:
        post_id = graphene.Int(required=True)

    def mutate(self, info, post_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")

        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")

        share, created = Share.objects.get_or_create(user=user, post=post)
        if not created:
            raise GraphQLError("You have already shared this post")

        return SharePost(share=share)


# MUTATION ROOT

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    delete_comment = DeleteComment.Field()
    like_post = LikePost.Field()
    unlike_post = UnlikePost.Field()
    share_post = SharePost.Field()

# SCHEMA
posts_schema = graphene.Schema(query=Query, mutation=Mutation)
