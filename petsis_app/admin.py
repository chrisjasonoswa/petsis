from django.contrib import admin
from .models import *

# Register your models here.

class InventoryItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user' ,'product', 'quantity', 'unit', 'price', 'category', 'item_img', 'status' )
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','order_id', 'customer_name', 'product','order_price','quantity', 'total')

class OrderLatestStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_obj', 'status', 'orderdatetime')

class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','order_id', 'supplier_name', 'product','supplier_product','order_price', 'quantity', 'total', 'order_created')

class SupplierOrderLatestStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_obj', 'status', 'orderdatetime')

class CategoryListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category')

class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notif', 'status')

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'act', 'act_datetime')

    

admin.site.register(User)
admin.site.register(CategoryList, CategoryListAdmin)
admin.site.register(InventoryItems, InventoryItemsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLatestStatus, OrderLatestStatusAdmin)
admin.site.register(SupplierOrder, SupplierOrderAdmin)
admin.site.register(SupplierOrderLatestStatus, SupplierOrderLatestStatusAdmin)
admin.site.register(Notifications, NotificationsAdmin)
admin.site.register(Activity, ActivityAdmin)