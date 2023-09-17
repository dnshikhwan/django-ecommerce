from django.db import models

from django.urls import reverse

# Create your models here.

# Category models


class Category(models.Model):
    name = models.CharField(max_length=250, db_index=True)
    # db_index = improve memory usage and faster look up during query
    slug = models.SlugField(max_length=250, unique=True)
    # unique = cannot duplicate or have the same slug

    class Meta:
        verbose_name_plural = 'categories'
        # Change the models from categorys to categories

    def __str__(self):
        return self.name
        # Return default attribute name
        # Instead return category (1), we return shoes

    def get_absolute_url(self):
        return reverse('list-category', args=[self.slug])


# Product models
class Product(models.Model):
    # Add foreign key
    category = models.ForeignKey(
        Category, related_name='product', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=250)
    brand = models.CharField(max_length=250, default='un-branded')
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.ImageField(upload_to='images/')

    class Meta:
        verbose_name_plural = 'products'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product-info', args=[self.slug])
