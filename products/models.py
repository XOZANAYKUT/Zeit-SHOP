from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    wishlist = models.ManyToManyField(User, related_name='favorite', blank=True)

    def __str__(self):
        return self.name
    
    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings.exists():
            return round(sum(rating.score for rating in ratings) / ratings.count(), 2)
        return 0

class Rating(models.Model):
    """
    Stores a single rating entry, related to :model:auth.User and :model:Product.
    """
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

    SCORE_CHOICES = [
        (ONE_STAR, '1 Star'),
        (TWO_STARS, '2 Stars'),
        (THREE_STARS, '3 Stars'),
        (FOUR_STARS, '4 Stars'),
        (FIVE_STARS, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(choices=SCORE_CHOICES)

    def _str_(self):
        return f'Rating {self.score} for {self.product.name} by {self.user.username}'


class Comment(models.Model):
    """
    Stores a single comment entry related to :model:auth.User
    and :model:products.Product.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]

    def _str_(self):
        return f"Comment {self.body} by {self.author}"