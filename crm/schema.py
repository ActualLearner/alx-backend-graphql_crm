import graphene
from crm.models import Product
from crm.types import ProductType


class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)

        products_to_return = list(low_stock_products)

        count = len(products_to_return)

        if count > 0:
            for product in products_to_return:
                product.stock += 10
                product.save()

            message = f"Successfully restocked {count} products."
            success = True
        else:
            message = "No low-stock products found to update."
            success = True

        return UpdateLowStockProducts(
            success=success, message=message, updated_products=products_to_return
        )


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query)
