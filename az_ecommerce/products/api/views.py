from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action

from az_ecommerce.products.api.serializers import (
    AddToCartSerializer,
    CartSerializer,
    CategorySerializer,
    FavoriteSerializer,
    ProductRetriveSerializer,
    ProductSerializer,
    RemoveItemSerializer,
)

from az_ecommerce.products.models import (
    Cart,
    CartItem,
    Category,
    Favorites,
    Product,
)


class CategoryViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ListModelMixin, RetrieveModelMixin,GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductRetriveSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title']
    
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        serializer_class=ProductSerializer,
        url_path="like"
    )
    def like_product(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(instance=product, context={"request":request})
        serializer.like_product(product)
        return Response(status=status.HTTP_201_CREATED)
    
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        serializer_class=ProductSerializer,
        url_path="unlike"
    )
    def unlike_product(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(instance=product, context={"request":request})
        serializer.unlike_product(product)
        return Response(status=status.HTTP_200_OK)

class FavoritesViewSet(ListModelMixin, GenericViewSet):
    queryset = Favorites.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorites.objects.filter(user=self.request.user)

class CartViewSet(ListModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == "create":
            return AddToCartSerializer
        if self.action == "remove_item":
            return RemoveItemSerializer
        return CartSerializer
    
    @action(
        detail=True,
        methods=["post"],
        url_path="remove-item",
    )
    def remove_item(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save
        return Response(status=status.HTTP_200_OK)

