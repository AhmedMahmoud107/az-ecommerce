from idna import valid_contextj
from requests import delete
from rest_framework import serializers

from az_ecommerce.products.models import (
    Cart,
    CartItem,
    Category,
    Product,
    Like,
    Favorites,
    Rating,
)


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "name",
            "image",
            "parent",
            "parent_name",
        ]

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None


class ProductSerializer(serializers.ModelSerializer):
    avg_rate = serializers.SerializerMethodField()
    tot_rate = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "price",
            "image",
            "size",
            "color",
            "quantity",
            "avg_rate",
            "tot_rate",
            "is_favorited",
            "is_liked"
        ]

    def get_avg_rate(self, obj):
        return obj.avg_rate()

    def get_tot_rate(self, obj):
        return obj.tot_rating()

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return Favorites.objects.filter(user=user, product=obj).exists()
    
    def get_is_liked(self, obj):
        user =self.context["request"].user
        return Like.objects.filter(user=user, product=obj)
    
    def like_product(self, product):
        user = self.context['request'].user
        like, created = Like.objects.get_or_create(user=user, product=product)
        favorite, _  = Favorites.objects.get_or_create(user=user, product=product)

        return like, created
    
    def unlike_product(self, product):
        user = self.context["request"].user
        Like.objects.filter(user=user, product=product).delete()
        Favorites.objects.filter(user=user, product=product).delete()

        return {"message": "unliked product and removed it from favorites"}
        
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        like = self.context['like']
        if like and like == 'like':
            self.like_product(instance)
        
        return instance

class ProductRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "price",
            "image",
            "size",
            "color",
            "quantity",
        ]

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductRetriveSerializer()
    class Meta:
        model = Favorites
        fields = [
            "product",
            "user",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductRetriveSerializer()
    class Meta:
        model = CartItem
        fields = [
            "product",
            "quantity",
            "tot_price",
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "items"
        ]

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        try:
            product = Product.objects.get(id=attrs["product_id"])
        except product.DoesNotExist:
            return serializers.ValidationError({"message": "product not found"})
        
        attrs["product"] = product
        return attrs
    
    def save(self, **kwargs):
        user = self.context["request"].user
        cart,_  = Cart.objects.get_or_create(user=user)
        product = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        item , created = CartItem.objects.get_or_create(cart=cart, product_id=product, quantity=quantity)
        if not created:
            item.quantity += quantity
        
        item.save()
    
class RemoveItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context["request"].user
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            raise serializers.ValidationError({"message": "cart is empty"})
        product_id = attrs["product_id"]
        item = CartItem.objects.filter(cart=cart, product_id=product_id)
        if not item:
            raise serializers.ValidationError({"message": "there is no item to delete"})
        
        attrs["item"] = item
        return attrs
    
    def save(self, **kwargs):
        item = self.validated_data["item"]
        item.delete()