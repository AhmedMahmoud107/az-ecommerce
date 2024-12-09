from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from az_ecommerce.users.api.views import UserAuthViewSet
from az_ecommerce.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("user", UserViewSet)
router.register("auth", UserAuthViewSet, basename="auth")


urlpatterns = [
    *router.urls,
]

app_name = "users"
