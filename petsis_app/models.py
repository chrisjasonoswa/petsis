from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import authenticate
import datetime
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    pass


class CategoryList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_categories") 
    category = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.category}" 

class InventoryItems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_inventory") 
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=10)
    price = models.FloatField()
    category = models.ForeignKey(CategoryList, on_delete=models.SET_NULL, blank=True, null=True)
    item_img = models.ImageField(blank=True, upload_to='images/')
    status = models.CharField(max_length=10, blank=True, default="visible")
    
    def __str__(self):
        return f"{self.product}" 



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_orders")
    order_id = models.CharField(max_length=500, editable=False)
    customer_name = models.CharField(max_length=30)
    product = models.ForeignKey(InventoryItems, on_delete=models.PROTECT, related_name="inventoryitems_orders")
    order_price = models.FloatField()
    quantity = models.IntegerField()
    total = models.FloatField()
    order_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} :  {self.order_id}" 
    

class OrderLatestStatus(models.Model):
    order_obj = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_latest_status")
    status = models.CharField(max_length=10)
    orderdatetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.orderdatetime = timezone.now()
        return super(OrderLatestStatus, self).save(*args, **kwargs)


class SupplierOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_supplier_orders")
    order_id = models.CharField(max_length=500, editable=False)
    supplier_name = models.CharField(max_length=30)
    product = models.ForeignKey(InventoryItems, on_delete=models.PROTECT, related_name="inventoryitems_supplier_orders")
    supplier_product = models.CharField(max_length=500)
    order_price = models.FloatField()
    quantity = models.IntegerField()
    total = models.FloatField()
    order_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.order_id}" 
    

class SupplierOrderLatestStatus(models.Model):
    order_obj = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name="supplier_order_latest_status")
    status = models.CharField(max_length=10)
    orderdatetime = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.orderdatetime = timezone.now()
        return super(SupplierOrderLatestStatus, self).save(*args, **kwargs)



class Activity(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_activity")
   act = models.CharField(max_length=250)
   act_datetime = models.DateTimeField(default=timezone.now)

class Notifications(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notif")
   notif = models.CharField(max_length=250)
   notif_type = models.CharField(max_length=20)
   status = models.CharField(max_length=10, default="unread")
   notif_datetime = models.DateTimeField(default=timezone.now)

