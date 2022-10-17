from .models import *
from django.contrib.auth import authenticate

def units_list():
    return sorted(['pc', 'kg', 'pack', 'set', 'pair'])

def increment_order_number(user):
    last_order = Order.objects.filter(user=user).order_by('id').last()
    if not last_order:
        return 'PtS0001'
    order_id = last_order.order_id
    order_int = int(order_id.split('PtS')[-1])
    new_order_int = order_int + 1
    new_order_id = 'PtS' + str(new_order_int).zfill(4)
    return new_order_id

def increment_p_order_number(user):
    last_order = SupplierOrder.objects.filter(user=user).order_by('id').last()
    if not last_order:
        return 'P0-PtS-0001'
    order_id = last_order.order_id
    order_int = int(order_id.split('P0-PtS-')[-1])
    new_order_int = order_int + 1
    new_order_id = 'P0-PtS-' + str(new_order_int).zfill(4)
    return new_order_id