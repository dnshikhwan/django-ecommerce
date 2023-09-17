from django.db import models

# get the user id of the authenticated user
from django.contrib.auth.models import User

# product model
from store.models import Product

# Shipping address model


class ShippingAddress(models.Model):

    # required fields
    full_name = models.CharField(max_length=300)
    email = models.EmailField(max_length=255)
    address1 = models.CharField(max_length=300)
    address2 = models.CharField(max_length=300)
    city = models.CharField(max_length=255)

    # this fields does not required (optional)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=255, null=True, blank=True)

    # foreign key for user id
    # authenticated and not authenticated user
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Shipping Address'

    # setup our own title
    def __str__(self):
        return 'Shipping Address - ' + str(self.id)

# order model


class Order(models.Model):

    full_name = models.CharField(max_length=300)
    email = models.EmailField(max_length=255)

    # comprised all in one
    shipping_address = models.TextField(max_length=10000)

    # total amount paid
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)

    # date order, set the time now()
    date_order = models.DateTimeField(auto_now_add=True)

    # foreign key, make sure to import user model
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)

    # save as Order - #1
    def __str__(self):
        return 'Order - #' + str(self.id)


# order item model, each product purchased has one model, keep track of what the user ordered
class OrderItem(models.Model):

    # FK that more involved
    # if the order model deleted, all the order items model also be deleted
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    # if product is deleted, also delete product in order item model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # foreign key
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return 'Order Item - #' + str(self.id)
