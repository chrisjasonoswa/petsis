from django.urls import path
from django.conf.urls.static import static
from . import views
from django.conf import settings
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("home", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("sales", views.sales, name="sales"),
    path("activity", views.activity, name="activity"),

    path("notifications<str:notif_id>", views.notif_read, name="notif_read"),
    path("notifications/read-all", views.notif_read_all, name="notif_read_all"),
    path("notifications/all", views.notif_all, name="notif_all"),

    path("orders", views.orders, name="orders"),
    path("orders/history", views.order_history, name="order_history"),
    path("orders/cancel/<str:order_id>", views.cancel, name="cancel"),
    path("orders/complete/<str:order_id>", views.complete, name="complete"),
    path("orders/update/<str:order_id>", views.update, name="update"),

    path("supplier-orders", views.supplier_orders, name="supplier_orders"),
    path("supplier-orders/history", views.supplier_orders_history, name="supplier_orders_history"),
    path("supplier-orders/update/<str:order_id>", views.update_supplier, name="update_supplier"),
    path("suppliers-orders/cancel/<str:order_id>", views.supplier_cancel, name="supplier_cancel"),
    path("suppliers-orders/complete/<str:order_id>", views.supplier_complete, name="supplier_complete"),
    
    path("inventory", views.inventory, name="inventory"),
    path("inventory/update", views.update_item, name="update_item"),
    path("inventory/remove/<int:item_id>", views.remove, name="remove"),
    path("inventory/<str:category_name>", views.category_view, name="category_view"),
    path("inventory/category/remove", views.category_remove, name="category_remove"),

    path("settings", views.settings, name="settings"),
    path("guide", views.user_guide, name="user_guide"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)