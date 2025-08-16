import graphene

class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_model(self, info):
        return "Hello, Graphql!"

schema = graphene.Schema(query=Query)
