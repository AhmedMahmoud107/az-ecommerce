from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

User = get_user_model()


class Category(MPTTModel):
    name = models.CharField(max_length=120)
    image = models.FileField(upload_to="categories-images/", blank=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Size(models.TextChoices):
    S = "small"
    M = "medium"
    L = "large"
    XL = "x-large"
    XXL = "xx-large"


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, choices=Size.choices, blank=True)
    image = models.FileField(upload_to="products_images/")
    color = models.CharField(max_length=120)
    quantity = models.IntegerField()
    like = models.ManyToManyField(User, related_name="liked_products", blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.title

    def avg_rate(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(ratings.aggregate(models.Avg("score"))["score__avg"], 1)
        return None

    def tot_rating(self):
        return self.ratings.count()


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.product} it is favorited by {self.user}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} likes {self.product}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.IntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"Rating{self.score} for {self.product.title} by {self.user.username}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="items"
    )
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def tot_price(self):
        return self.product.price * self.quantity