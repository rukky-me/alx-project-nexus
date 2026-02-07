import graphene
from posts.schema import Query as PostsQuery, Mutation as PostsMutation
from analytics.schema import Query as AnalyticsQuery, Mutation as AnalyticsMutation
from interactions.schema import Query as InteractionsQuery, Mutation as InteractionsMutation

class Query(PostsQuery, AnalyticsQuery, InteractionsQuery, graphene.ObjectType):
    pass

class Mutation(PostsMutation, AnalyticsMutation, InteractionsMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
