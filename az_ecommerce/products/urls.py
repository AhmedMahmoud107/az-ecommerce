from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from az_ecommerce.products.api.views import (
    CartViewSet,
    CategoryViewSet,
    ProductViewSet,
    FavoritesViewSet
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("favorites", FavoritesViewSet)
router.register("cart", CartViewSet, basename="cart")



urlpatterns = [
    *router.urls,
]

app_name = "products"
