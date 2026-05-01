from django.db import models
from cloudinary.models import CloudinaryField


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image = CloudinaryField('image',folder = 'category/images')
    description = models.TextField()
    is_active = models.BooleanField(
        choices=[(True, "Active"), (False, "Inactive")], default=True
    )
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250)
    descirption = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(choices=[(True, "Active"), (False, "Inactive")])
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    