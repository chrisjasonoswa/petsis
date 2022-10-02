from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from .utils import * 
from django.db.models import Sum, Count, F
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth, TruncYear, ExtractMonth
import calendar


# Create your views here.

def homepage(request, succ_mssg=None):
    if request.user.is_authenticated:
        return redirect("index")

    context ={
        "succ_mssg": succ_mssg,
    }
    return render(request, "petsis_app/homepage.html", context)

@login_required
def index(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Get top selling products
    today = datetime.today()
    thirty_days_ago = today - timedelta(days=30)
    top_selling_products = OrderLatestStatus.objects.filter(order_obj__user= user,orderdatetime__range=[thirty_days_ago, today], status="Completed").values('order_obj__product__product','order_obj__product__quantity', 'order_obj__product__price','order_obj__product__item_img','order_obj__product__unit' ).annotate(sold = Sum('order_obj__quantity')).order_by('-sold')[:5]

    #Recent sales within the week
    week_ago = today - timedelta(days=7)
    rec_sales = OrderLatestStatus.objects.filter(order_obj__user= user, orderdatetime__range=[week_ago, today], status="Completed").order_by('-orderdatetime')[:10]
    
    #Get total number of items products
    no_items = user.user_inventory.filter(status="visible").count()

    #Get number of categories
    no_categories = user.user_categories.all().count()

    #Get number of stocks of the items
    no_overall_quantity = user.user_inventory.filter(status="visible").aggregate(overall_quantity = Sum('quantity'))['overall_quantity']

    #Get total price of all items relative to their quantity
    total_price_all = user.user_inventory.filter(status="visible").aggregate(total_price = Sum(F('price') * F('quantity'), output_field=models.FloatField()))['total_price']

    #Get Recent Sales : Completed
    completed_orders = OrderLatestStatus.objects.filter(status="Completed", order_obj__user=user).order_by('-orderdatetime')[:10]

    #Get Recent Activity up to 10 
    rec_act = Activity.objects.filter(user=user).order_by('-id')[:10]

    #Get number of orders
    order_labels = []
    orders = []
    order_month_set = OrderLatestStatus.objects.filter(order_obj__user=user, status="Completed").annotate(month = ExtractMonth('orderdatetime')).values('month').annotate(count_orders = Count('order_obj__id')).values('month','count_orders').order_by('-month')[:5]
    for order in order_month_set:
        order_labels.append(calendar.month_name[int(order['month'])])
        orders.append(order['count_orders'])
    order_labels.reverse()
    orders.reverse()

    #Get sales every month
    labels_sales = []
    sales_count = []
    sales_month_set = OrderLatestStatus.objects.filter(order_obj__user=user, status="Completed").annotate(month = ExtractMonth('orderdatetime')).values('month').annotate(sales = Sum('order_obj__total')).values('month','sales').order_by('-month')[:5]
    for sale in sales_month_set:
        labels_sales.append(calendar.month_name[int(sale['month'])])
        sales_count.append(sale['sales'])
    labels_sales.reverse()
    sales_count.reverse()

    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context = {
        "top_selling_products": top_selling_products,
        "no_items": no_items,
        "no_categories": no_categories,
        "no_overall_quantity": no_overall_quantity,
        "total_price_all": total_price_all,
        "completed_orders": completed_orders,
        "rec_sales" : rec_sales,
        "rec_act": rec_act,
        "order_labels": order_labels,
        "orders": orders,
        "labels_sales": labels_sales,
        "sales_count": sales_count,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }
    return render(request, "petsis_app/index.html", context)

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "petsis_app/login.html", {
                "message": "Invalid username and/or password."
            })

    else:
        return render(request, "petsis_app/login.html")

def logout_view(request):
    if request.user.is_authenticated:  
        logout(request)
        succ_mssg = "You are successfully logged out!"
        return homepage(request, succ_mssg=succ_mssg)
    else:
        return redirect("homepage")

def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "petsis_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "petsis_app/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return redirect("login")

    else:
        return render(request, "petsis_app/register.html")


@login_required
def sales(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    sales_total = OrderLatestStatus.objects.filter(order_obj__user= user, status="Completed").aggregate(total = Sum('order_obj__total'))
    sales_list = OrderLatestStatus.objects.filter(order_obj__user= user, status="Completed").order_by('-orderdatetime', '-order_obj__order_id')
    context ={
        "sales_list": sales_list,
        "sales_total": sales_total['total'],
    }
    return render(request, "petsis_app/sales.html", context)

@login_required
def activity(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    rec_act = Activity.objects.filter(user=user).order_by('-id')
    context ={
        "rec_act": rec_act,
    }
    return render(request, "petsis_app/recent_activity.html", context)


@login_required
def inventory(request, err_mssg=None, succ_mssg=None, item_list = None, cat_filter=None):
    
    username = request.user.get_username()
    user = User.objects.get(username=username)

    if item_list == None:
        item_list = InventoryItems.objects.filter(user=user, status="visible").order_by('product')


    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context = {
        "units": units_list(),
        "category_list": user.user_categories.all().values_list('category', flat=True).order_by('category'),
        "item_list": item_list,
        "err_mssg": err_mssg,
        "succ_mssg": succ_mssg,
        "cat_filter": cat_filter,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }

    inv_items = InventoryItems.objects.all()
    if request.method == "POST":
        
        #Adding Categories
        if 'add_category' in request.POST:
            new_category = request.POST["add_category"]
            new_category = new_category[0].upper() + new_category[1:]
            try:
                if new_category in context['category_list']:
                    raise IntegrityError
                create_category = CategoryList(user=user, category=new_category)
                create_category.save()
                category_mssg_success = "Category Added Successfully!"

                
                #Add to recent activity - add category
                act = f"New Category:&nbsp;<a href='/inventory/{new_category}'>{new_category} </a>&nbsp;is <span style='color:rgb(33, 185, 109);'>added</span> to the list of categories."
                new_act = Activity(user=user, act=act)
                new_act.save()

                #Redirect to the inventory
                request.method="GET"
                return inventory(request, succ_mssg=category_mssg_success )

            except (IntegrityError, TypeError):
                category_mssg_failed = "Category Already Exists!"
                request.method="GET"
                return inventory(request, err_mssg=category_mssg_failed)

        #Adding Items
        elif 'add_product' in request.POST:
            new_item = request.POST["add_product"].title()
            category = None
            item_img = 'images/item_default_png.png'

            try:
                InventoryItems.objects.get(product=new_item, user=user, status="visible")
                add_item_err_mssg = "Product Already Exists. Just add quantity to the existing product"
                request.method="GET"
                return inventory(request, err_mssg=add_item_err_mssg)       

            except InventoryItems.DoesNotExist:
                if 'category' in request.POST:
                    category = request.POST["category"]
                    category = CategoryList.objects.get(user=user, category=category)
                if  'item_img'in request.FILES:
                    item_img = request.FILES['item_img']
                    _ , item_img_ext = str(item_img.name).rsplit(".", 1)
                    item_img.name = new_item + "_" + username + "." + item_img_ext

                add_item = InventoryItems(user=user, product= new_item, quantity= request.POST["quantity"], 
                                unit=request.POST["unit"], price=request.POST["price"],
                                category=category, item_img=item_img)
                add_item.save()      
                add_item_mssg = "Item Added Successfully"

                #Add to recent activity - add item
                act = f"New Item:&nbsp;<a href='/inventory'>{new_item} </a>&nbsp;is <span style='color:rgb(33, 185, 109);'>added</span> to the inventory."
                new_act = Activity(user=user, act=act)
                new_act.save()

                request.method="GET"
                return inventory(request, succ_mssg=add_item_mssg)                 

    else:
        return render(request, "petsis_app/inventory.html", context)

@login_required
def category_view(request, category_name):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    

    category_list = user.user_categories.all().values_list('category', flat=True).order_by('category')
    item_list = InventoryItems.objects.filter(user=user, category__category= category_name, status='visible').order_by('product')

    request.method = "GET"
    return inventory(request, item_list = item_list, cat_filter=category_name) 

@login_required
def category_remove(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    if request.method == "POST" and 'category' in request.POST:
        category = user.user_categories.get(category = request.POST['category'])
        category.delete()

    #Add to recent activity - remove category
    act = f"Category:&nbsp;<a>{request.POST['category']} </a>&nbsp;is <span style='color:red;'>removed</span> from the list of categories."
    new_act = Activity(user=user, act=act)
    new_act.save()

    request.method="GET"
    return inventory(request, succ_mssg="Category Successfully Deleted!.")


@login_required
def update_item(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    if request.method == "POST":
        item_id = int(request.POST['item_id'])
        product = request.POST['product']
        quantity = int(request.POST['quantity'])
        unit = request.POST['unit']
        price = float(request.POST['price'])

        if not 'category' in request.POST:
            category = None
        else:
            category = CategoryList.objects.get(user=user, category=request.POST['category'])
        inv_item = InventoryItems.objects.get(user=user, id=item_id)

        #Update info
        inv_item.product = product
        inv_item.quantity = quantity
        inv_item.unit = unit
        inv_item.price = price
        inv_item.category = category


        #Update image if an image is uploaded
        if  'item_img' in request.FILES:
            item_img = request.FILES['item_img']
            _ , item_img_ext = str(item_img.name).rsplit(".", 1)
            item_img.name = product + "_" + username + "." + item_img_ext

            inv_item.item_img = item_img
        
        #Save inventory item
        inv_item.save()

        #Add to recent activity - update item
        act = f"Item: <a href='/inventory'>{product} </a>&nbsp;details are <span style='color: rgb(18, 214, 198);'>updated</span>."
        new_act = Activity(user=user, act=act)
        new_act.save()
        

        request.method="GET"
        return inventory(request, succ_mssg=f"{inv_item.product} Successfully Updated!.")


@login_required()     
def remove(request, item_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Cancel all pending orders associated with the item
    inv_item = InventoryItems.objects.get(user=user, id=item_id)
    order_pending = OrderLatestStatus.objects.filter(order_obj__product=inv_item, status="Pending")
    order_pending.update(status="Cancelled")

    #Change item status to hidden
    inv_item.quantity = 0
    inv_item.status = "hidden"
    inv_item.save()

    #Get the item product name before deletion
    product_name = inv_item.product

    #Change Item Name
    del_date = datetime.now()
    del_date = del_date.strftime("%b %d %Y, %H:%M")
    inv_item.product = f"{inv_item.product} (Deleted: {del_date}) "
    inv_item.save()

    #Add to recent activity - remove item
    act = f"<a href='/inventory'>{inv_item.product} </a>&nbsp; is <span style='color:red;'>removed</span> in the inventory."
    new_act = Activity(user=user, act=act)
    new_act.save()

    request.method="GET"
    return inventory(request, succ_mssg=f"{product_name} Successfully Deleted!.")  



@login_required
def orders(request, err_message=None, complete_mssg=None):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    #Load the Select Product List
    product_list = InventoryItems.objects.filter(user=user, status="visible")

    #Load Pending Orders
    #Paginator
    pending_orders = OrderLatestStatus.objects.filter(status="Pending", order_obj__user=user).order_by('-orderdatetime', '-order_obj__id')
    #p = Paginator(pending_orders, 5)
    #page = request.GET.get('page')
    #p_orders = p.get_page(page)

    #Load Cancelled Orders
    cancelled_orders = OrderLatestStatus.objects.filter(status="Cancelled", order_obj__user=user).order_by('-orderdatetime', '-order_obj__order_id')[:10]

    #Load Completed Orders
    completed_orders = OrderLatestStatus.objects.filter(status="Completed", order_obj__user=user).order_by('-orderdatetime', '-order_obj__order_id')[:10]
    
    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context ={ 
        "product_list": product_list,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "completed_orders": completed_orders,
        "err_message": err_message,
        "complete_mssg": complete_mssg,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }

    if request.method == "POST":
        product = InventoryItems.objects.get(user=user, product=request.POST["product"], status="visible")
        quantity = int(request.POST["quantity"])
        customer = request.POST["customer"] 
        total = product.price * float(quantity)

        #Minus quantity sa inventoryitems quantity
        if quantity > product.quantity:
            add_order_err = "Insufficient Quantity. Order Failed!"
            request.method = "GET"
            return orders(request, err_message=add_order_err)

        #Make Order
        add_order = Order(user=user, order_id=increment_order_number(user),customer_name=customer, product=product, quantity=quantity, order_price=product.price,   total=total)
        add_order.save()
        add_order_obj = Order.objects.get(id=add_order.id)

        product.quantity = product.quantity - quantity
        product.save()

        #Add Entry to the OrderLatest Status
        add_ord_status = OrderLatestStatus(order_obj=add_order_obj, status="Pending")
        add_ord_status.save()

        #Add to recent activity - new active order
        act = f"New Customer Order:&nbsp;<a href='/orders'>{add_order_obj.order_id} </a>&nbsp;with&nbsp;{quantity}{product.unit}s of <a href='/inventory'>{product.product}</a> is now  <span style='color:rgb(231, 201, 29);'>pending</span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        #Add to Notifications if stock is low or out of stock
        if product.quantity == 0:
            notif = f"<b>{product.product}</b>&nbsp;is Out of Stock"
            Notifications.objects.create(user=user, notif=notif, notif_type="danger")
        elif product.quantity < 30:
            notif = f"<b>{product.product}</b>&nbsp;is Low on Stock"
            Notifications.objects.create(user=user, notif=notif, notif_type="warning")

        add_order_success = "Order Successfully Added!"
        request.method = "GET"
        return orders(request, complete_mssg=add_order_success)

       
    else:
        return render(request, "petsis_app/orders.html", context)

@login_required
def order_history(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    transaction_history = OrderLatestStatus.objects.filter(order_obj__user=user).order_by('-id')
    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context = {
        "transaction_history": transaction_history,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }
    return render(request, "petsis_app/order_history.html", context)

@login_required
def cancel(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    if request.method == "POST":
        order_obj = Order.objects.get(order_id=order_id, user=user)

        #Add to the quantity again
        restore_quantity = InventoryItems.objects.get(user=user, product=order_obj.product.product, status="visible")
        restore_quantity.quantity = restore_quantity.quantity + order_obj.quantity
        restore_quantity.save()
        
        cancel_order = OrderLatestStatus.objects.get(order_obj=order_obj)
        cancel_order.status="Cancelled"
        cancel_order.save()
        cancel_order_mssg = "Order Successfully Cancelled!" 

        #Add to recent activity - new active order
        act = f"Customer Order:&nbsp;<a href='/orders'>{order_obj.order_id} </a>&nbsp;with {order_obj.quantity}{order_obj.product.unit}s of <a href='/inventory'>{order_obj.product.product}</a> is <span style='color:red;'>cancelled<span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        request.method = "GET"
        return orders(request, complete_mssg=cancel_order_mssg)

@login_required
def complete(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    if request.method == "POST":
        order_obj = Order.objects.get(order_id=order_id, user=user)
        update_order = OrderLatestStatus.objects.get(order_obj=order_obj)
        update_order.status="Completed"
        update_order.save()
        complete_mssg = "Order Completed."

        #Add to recent activity - new completed order
        act = f"Customer Order:&nbsp;<a href='/orders'>{order_obj.order_id}</a>&nbsp;with {order_obj.quantity}{order_obj.product.unit}s of <a href='/inventory'>{order_obj.product.product}</a> is <span style='color:rgb(33, 185, 109);'>completed<span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        request.method = "GET"
        return orders(request, complete_mssg=complete_mssg)

@login_required
def update(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    if request.method == "POST":

        #Order Table
        prev_order = Order.objects.get(user=user, order_id=request.POST['prev_order'])
        #Inventory Item Product
        curr_product = InventoryItems.objects.get(user=user, product=request.POST['curr_product'], status="visible") 
        
        customer = request.POST['customer']
        quantity = int(request.POST['quantity'])
        price = float(request.POST['price']) 


        #If product is changed
        if not prev_order.product == curr_product:
            #Restore quantity to the previous order item
            prev_order.product.quantity += prev_order.quantity
            prev_order.product.save()

            #Check if inventory items quantity is available or sufficient
            if curr_product.quantity < quantity:
                up_err_message = "ORDER FAILED! The selected product has insufficient quantity to satisfy the Order." 
                request.method = "GET"
                return orders(request, up_err_message)
                #Return Err Mssg

            #Deduct quantity to the new inventory product
            curr_product.quantity -= quantity
            curr_product.save()
                

        #If product is not changed
        else:
            #If quantity is changed
            if not prev_order.quantity == quantity:
                qt_chng = int(prev_order.quantity - quantity)

                #Change the inventory item quantity
                prev_order.product.quantity = prev_order.product.quantity + qt_chng
                 
                #Check if quantity will not equal to less than 0
                if prev_order.product.quantity < 0:
                    up_err_message = "ORDER FAILED! The selected product has insufficient quantity to satisfy the Order." 
                    request.method = "GET"
                    return orders(request, err_message = up_err_message)

                #Save when quantity is sufficient
                prev_order.product.save()

        #Change order information
        prev_order.customer_name = customer
        prev_order.product = curr_product
        prev_order.order_price = price
        prev_order.quantity = quantity
        prev_order.total = price * quantity
        prev_order.save()

        #Add to recent activity - update order
        act = f"Customer Order:&nbsp;<a href='/orders'>{prev_order.order_id}</a> is <span style='color: rgb(18, 214, 198);'>updated</span>."
        new_act = Activity(user=user, act=act)
        new_act.save()


        request.method = "GET"
        return orders(request, complete_mssg="Order Sucessfully Updated.")

@login_required
def settings(request, succ_mssg=None, err_mssg=None):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    
    if request.method == "POST":
        #Update New Username
        if 'new_username' in request.POST:
            try:
                user.username = request.POST['new_username']
                user.save()
                #Update session
                request.user.username = user.username
                update_session_auth_hash(request, user)
                request.method = "GET"
                return settings(request, succ_mssg="Username Successfully Updated")
            except IntegrityError:
                request.method = "GET"
                return settings(request, err_mssg="New Username Already Exists")

        #Update New Email
        elif 'new_email' in request.POST:
            user.email = request.POST['new_email']
            user.save()
            #Update session
            update_session_auth_hash(request, user)
            request.method = "GET"
            return settings(request, succ_mssg="Email Successfully Updated")

        #Update New Password
        elif 'new_password' in request.POST:

            #check if current password input matches with the users current password
            if not user.check_password(request.POST['curr_password']):
                request.method = "GET"
                return settings(request, err_mssg="Current Password Validation Failed!")
            else:
                if request.POST['new_password'] == request.POST['confirmation']:
                    user.set_password(request.POST['new_password'])
                    user.save()

                    #Update session
                    update_session_auth_hash(request, user)
                    request.method = "GET"
                    return settings(request, succ_mssg="Password Successfully Updated")
                else:
                    request.method = "GET"
                    return settings(request, err_mssg="Passwords did not match!")
                
                
    else:
        #Get User Notifications
        notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
        no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
        if no_active_notif > 99:
            no_active_notif = "99+"
        
        context = {
            "user_obj": user,
            "err_mssg": err_mssg,
            "succ_mssg": succ_mssg,
            "notifications": notifications,
            "no_active_notif": no_active_notif,
        }
        return render(request, "petsis_app/settings.html",context)

@login_required
def user_guide(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context ={
        "username":username,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }
    return render(request, "petsis_app/usage.html", context)


@login_required
def supplier_orders(request, err_message=None, complete_mssg=None):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Load the Select Product List
    product_list = InventoryItems.objects.filter(user=user, status="visible")

    #Load Pending Orders
    pending_orders = SupplierOrderLatestStatus.objects.filter(status="Pending", order_obj__user=user).order_by('-orderdatetime', '-order_obj__id')

    #Load Cancelled Orders
    cancelled_orders = SupplierOrderLatestStatus.objects.filter(status="Cancelled", order_obj__user=user).order_by('-orderdatetime', '-order_obj__order_id')[:10]

    #Load Completed Orders
    completed_orders = SupplierOrderLatestStatus.objects.filter(status="Completed", order_obj__user=user).order_by('-orderdatetime', '-order_obj__order_id')[:10]
    
    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context ={ 
        "product_list": product_list,
        "pending_orders": pending_orders,
        "cancelled_orders": cancelled_orders,
        "completed_orders": completed_orders,
        "err_message": err_message,
        "complete_mssg": complete_mssg,
        "notifications": notifications,
        "no_active_notif": no_active_notif
    }

    if request.method == "POST":
        product = InventoryItems.objects.get(user=user, product=request.POST["product"], status="visible")
        quantity = int(request.POST["quantity"])
        supplier = request.POST["supplier"] 
        total = quantity * float(request.POST["price"])
        supplier_product = request.POST["supplier_product"]
        order_price = float(request.POST["price"])


        #Make Supplier Order
        add_order = SupplierOrder(user=user, order_id=increment_p_order_number(user), supplier_name=supplier, product=product, supplier_product=supplier_product,   order_price=order_price, quantity=quantity, total=total)
        add_order.save()
        add_order_obj = SupplierOrder.objects.get(id=add_order.id)
        
        #Add Entry to the SupplierOrderLatest Status
        supp_ord  = SupplierOrderLatestStatus.objects.create(order_obj=add_order, status="Pending")

        #Add to recent activity - new active purchase order
        act = f"New Purchase Order:&nbsp;<a href='/supplier-orders'>{add_order_obj.order_id} </a>&nbsp;with&nbsp;{quantity}{product.unit}s of {supplier_product} from {supplier} is now <span style='color:rgb(231, 201, 29);'>pending</span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        add_order_success = "Order Successfully Added!"
        request.method = "GET"
        return supplier_orders(request, complete_mssg=add_order_success)

       
    else:
        return render(request, "petsis_app/supplier_orders.html", context)

@login_required
def update_supplier(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    if request.method == "POST":
        supplier_order = SupplierOrder.objects.get(user=user, order_id=request.POST['prev_order'])
        product = InventoryItems.objects.get(user=user, product=request.POST["curr_product"])

        #Change order information
        supplier_order.supplier_name = request.POST["supplier_name"]
        supplier_order.product = product
        supplier_order.supplier_product = request.POST["supplier_product"]
        supplier_order.order_price = request.POST["price"]
        supplier_order.quantity = request.POST["quantity"]
        supplier_order.save()

        #Add to recent activity - update supplier order
        act = f"Purchase Order:&nbsp;<a href='/supplier-orders'>{supplier_order.order_id}</a> is <span style='color: rgb(18, 214, 198);'>updated</span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        request.method = "GET"
        return supplier_orders(request, complete_mssg="Order Sucessfully Updated.")

@login_required
def supplier_cancel(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    if request.method == "POST":
        order_obj = SupplierOrder.objects.get(user=user, order_id=order_id) 
        order = SupplierOrderLatestStatus.objects.get(order_obj=order_obj)
        order.status ="Cancelled"
        order.save()
    
        cancel_order_mssg = "Order Successfully Cancelled!"

        #Add to recent activity - new active order
        act = f"Purchase Order:&nbsp;<a href='/supplier-orders'>{order.order_obj.order_id} </a>&nbsp;with {order.order_obj.quantity}{order.order_obj.product.unit}s of {order.order_obj.supplier_product} from {order.order_obj.supplier_name} is <span style='color:red;'>cancelled<span>."
        new_act = Activity(user=user, act=act)
        new_act.save()

        request.method = "GET"
        return supplier_orders(request, complete_mssg=cancel_order_mssg)

@login_required
def supplier_complete(request, order_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    if request.method == "POST":
        order_obj = SupplierOrder.objects.get(order_id=order_id, user=user)
        update_order = SupplierOrderLatestStatus.objects.get(order_obj=order_obj)
        update_order.status="Completed"
        update_order.save()
        complete_mssg = "Order Completed."


        #Restock the quantity to the selected product
        product = InventoryItems.objects.get(user=user, id=order_obj.product.id)
        product.quantity += order_obj.quantity
        product.save()

        #Add to recent activity - new completed order
        act = f"Purchase Order:&nbsp;<a href='/supplier-orders'>{order_obj.order_id}</a>&nbsp;with {order_obj.quantity}{order_obj.product.unit}s\
        of {order_obj.supplier_product} from {order_obj.supplier_name} is <span style='color:rgb(33, 185, 109);'>completed</span>. Item <a href='/inventory'>{order_obj.product.product}</a> is restocked"
        new_act = Activity(user=user, act=act)
        new_act.save()

        #Add to Notifications
        notif = f"<b>{order_obj.product.product}</b>&nbsp;is restocked by {order_obj.quantity}{order_obj.product.unit}s"
        Notifications.objects.create(user=user, notif=notif, notif_type="success")

        request.method = "GET"
        return supplier_orders(request, complete_mssg=complete_mssg)

@login_required
def supplier_orders_history(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    transaction_history = SupplierOrderLatestStatus.objects.filter(order_obj__user=user).order_by('-id')

    #Get User Notifications
    notifications = Notifications.objects.filter(user=user).order_by('-id')[:10]
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()
    if no_active_notif > 99:
        no_active_notif = "99+"

    context = {
        "transaction_history": transaction_history,
        "notifications": notifications,
        "no_active_notif": no_active_notif,
    }
    return render(request, "petsis_app/supplier_orders_history.html", context)

@login_required
def notif_read(request, notif_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    notif_obj = Notifications.objects.get(user=user, id=notif_id)
    notif_obj.status = "read"
    notif_obj.save()

    return redirect("inventory")

@login_required
def notif_read_all(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Set all Notifications to Read
    Notifications.objects.filter(user=user).update(status="read")
    return redirect(request.META['HTTP_REFERER'])

@login_required
def notif_all(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)

    #Get User Notifications
    notifications_recent = Notifications.objects.filter(user=user).order_by('-id')[:10]
    notifications_all = Notifications.objects.filter(user=user).order_by('-id')
    no_active_notif = Notifications.objects.filter(user=user, status="unread").count()

    context = {
        "notifications": notifications_recent,
        "notifications_all": notifications_all,
        "no_active_notif": no_active_notif,
    }

    return render(request, "petsis_app/notifications.html", context)