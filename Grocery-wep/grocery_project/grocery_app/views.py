from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Product, Order, Payment, Cart, Shipment  , Category , Supplier  ,ProductPerformanceReport
from .forms import CustomerRegistrationForm   ,  ProductForm   , SupplierForm

from django.utils import timezone


from .forms import CategoryForm
from django.db.models import Q


from django.shortcuts import redirect, get_object_or_404



from .utils import transfer_cart_to_order





User = get_user_model()  # Custom user model support

# ---------------------- HOME & BASE PAGES ----------------------


from django.shortcuts import render
from .models import Product  # Import your Product model

def home(request):
    products = Product.objects.filter(stock_quantity__gt=0).order_by('-created_at')[:6]
    return render(request, "home.html", {'products': products})


def base(request):
    return render(request, "base.html")

def about(request):
    return render(request, "about.html")

# def contact(request):
#     return render(request, "contact.html")


from django.shortcuts import render, redirect, get_object_or_404
from .models import Contact
from django.contrib.auth.decorators import login_required

@login_required
def view_contact_messages(request):
    query = request.GET.get('search', '')
    messages = Contact.objects.all()
    if query:
        messages = messages.filter(name__icontains=query)
    messages = messages.order_by('-sent_at')
    return render(request, 'contact_messages.html', {'messages': messages, 'search_query': query})

@login_required
def delete_contact_message(request, pk):
    message = get_object_or_404(Contact, pk=pk)
    message.delete()
    return redirect('view_contact_messages')







from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent!")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})









from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Contact

@login_required
def view_contact_messages(request):
    messages = Contact.objects.order_by('-sent_at')
    return render(request, 'contact_messages.html', {'messages': messages})





# ---------------------- USER REGISTRATION ----------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.role = "Customer"
            user.save()
            login(request, user)
            return redirect("customer_dashboard")

    return render(request, "register.html")

# ---------------------- USER LOGIN ----------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, "role"):
            login(request, user)
            return redirect(f"{user.role.lower()}_dashboard")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "login.html")

# ---------------------- USER LOGOUT ----------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

# ---------------------- ROLE-SPECIFIC LOGIN PAGES ----------------------
def admin_login(request):
    return render(request, "admin_login.html")

def seller_login(request):
    return render(request, "login_seller.html")

def customer_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and user.role == "Customer":
            login(request, user)
            return redirect("customer_dashboard")
        else:
            messages.error(request, "Invalid credentials or not a customer account.")

    return render(request, "customer_login.html")

# ---------------------- ROLE-BASED DASHBOARDS ----------------------


@login_required
@user_passes_test(lambda user: hasattr(user, "role") and user.role == "Admin")
def admin_dashboard(request):
    context = {
        "orders_count": Order.objects.count(),
        "products_count": Product.objects.count(),
        "users_count": User.objects.count(),
        "payments_count": Payment.objects.count(),
    }
    return render(request, "admin_dashboard.html", context)






@login_required
@user_passes_test(lambda user: hasattr(user, "role") and user.role == "Seller")
def seller_dashboard(request):
    seller = request.user
    context = {
        "seller_name": seller.username,
        "total_products": Product.objects.filter(seller=seller).count(),
        "total_sales": Order.objects.filter(user=seller).count(),
        "low_stock_items": Product.objects.filter(seller=seller, stock_quantity__lt=5).count(),
    }
    return render(request, "seller_dashboard.html", context)






@login_required
@user_passes_test(lambda user: hasattr(user, "role") and user.role == "Customer")
def customer_dashboard(request):
    context = {
        "total_products": Product.objects.filter(stock_quantity__gt=0).count(),
        "recent_orders": Order.objects.filter(user=request.user).count(),
    }
    return render(request, "customer_dashboard.html", context)

# ---------------------- SELLER REGISTRATION ----------------------
def register_seller(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
        else:
            seller = User.objects.create_user(username=username, email=email, password=password)
            seller.role = "Seller"
            seller.phone = phone
            seller.save()
            login(request, seller)
            messages.success(request, "Seller account created successfully!")
            return redirect("seller_dashboard")

    return render(request, "register_seller.html")

# ---------------------- SELLER LOGOUT ----------------------
@login_required
def logout_seller(request):
    logout(request)
    return redirect("seller_login")

# ---------------------- SELLER PASSWORD RESET ----------------------
def reset_seller_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        seller = User.objects.filter(email=email, role="Seller").first()

        if seller:
            seller.set_password("new_secure_password")
            seller.save()
            messages.success(request, "Password reset. Use 'new_secure_password' to log in.")
            return redirect("seller_login")
        else:
            messages.error(request, "Seller account not found.")

    return render(request, "reset_seller_password.html")

# ---------------------- CUSTOMER MANAGEMENT ----------------------
def customer_register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "Customer"
            user.save()
            login(request, user)
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("customer_dashboard")
        else:
            print(form.errors)  # Debugging validation errors
            messages.error(request, "Registration failed. Please check the form inputs.")
    else:
        form = CustomerRegistrationForm()

    return render(request, "customer_register.html", {"form": form})

def reset_customer_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        customer = User.objects.filter(email=email, role="Customer").first()

        if customer:
            customer.set_password("new_secure_password")
            customer.save()
            messages.success(request, "Password reset. Use 'new_secure_password' to log in.")
            return redirect("customer_login")
        else:
            messages.error(request, "Customer account not found.")

    return render(request, "reset_customer_password.html")








def login_seller(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, "role") and user.role == "Seller":
            login(request, user)
            return redirect("seller_dashboard")
        else:
            messages.error(request, "Invalid credentials or not a seller account.")

    return render(request, "login_seller.html")


def pending_orders(request):
    orders = Order.objects.filter(order_status="Pending")
    return render(request, "pending_orders.html", {"orders": orders})





def view_sales(request):
    sales = Order.objects.filter(order_status="Completed")
    return render(request, "view_sales.html", {"sales": sales})



def shipment(request):
    shipments = Shipment.objects.all()
    return render(request, "shipment.html", {"shipments": shipments})



@login_required
def browse_products(request):
    products = Product.objects.filter(stock_quantity__gt=0)  # ✅ Fetch available products
    return render(request, "browse_products.html", {"products": products})


# @login_required
# def browse_products(request):
#     query = request.GET.get("search")
#     print("Search input:", query)  # Debug line

#     if query:
#         products = Product.objects.filter(stock_quantity__gt=0, name__icontains=query)
#     else:
#         products = Product.objects.filter(stock_quantity__gt=0)

#     print("Found products:", products)  # Debug line
#     return render(request, "browse_products.html", {"products": products})




# @login_required
# def cart_view(request):
#     cart_items = Cart.objects.filter(user=request.user)  # ✅ Fetch user's cart items
#     return render(request, "cart_view.html", {"cart_items": cart_items})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Cart, Order

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    item_totals = []
    for item in cart_items:
        item_totals.append({
            "item": item,
            "total": item.product.price * item.quantity
        })

    return render(request, "cart_view.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "item_totals": item_totals
    })

@login_required
def orders(request):
    customer_orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders.html", {"orders": customer_orders})

@login_required
def checkout(request):
    # This assumes the checkout page is used to inform or confirm payment details.
    return render(request, "checkout.html")


@login_required
def manage_account(request):
    return render(request, "manage_account.html")





@login_required
def track_shipment(request):
    shipments = Shipment.objects.filter(user=request.user)  # ✅ Fetch user's shipments
    return render(request, "track_shipment.html", {"shipments": shipments})







@login_required
def customer_master(request):
    return render(request, "customer_master.html")





def customer_logout(request):
    logout(request)  # ✅ Logs the user out
    return redirect("customer_login")  # ✅ Redirects to login page






from django.shortcuts import render
from .models import Product

def browse_products(request):
    products = Product.objects.filter(stock_quantity__gt=0)  # ✅ Only show products in stock
    return render(request, "browse_products.html", {"products": products})





def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # ✅ Get the product
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)  # ✅ Add to cart
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart_view")  # ✅ Redirect to cart page








from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Product

@login_required
@user_passes_test(lambda user: user.role == "Seller")
def manage_products(request):
    query = request.GET.get("q")
    products = Product.objects.all().select_related("category", "supplier", "seller")

    if query:
        products = products.filter(name__icontains=query)

    return render(request, "manage_products.html", {"products": products})








@login_required
@user_passes_test(lambda u: u.role == "Seller")
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("manage_products")
    else:
        form = ProductForm(instance=product)

    return render(request, "edit_product.html", {"form": form, "product": product})


@login_required
@user_passes_test(lambda u: u.role == "Seller")
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect("manage_products")

    return render(request, "confirm_delete.html", {"product": product})






@login_required
@user_passes_test(lambda u: u.role == "Seller")
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect("manage_products")
    else:
        form = ProductForm()
    return render(request, "add_product.html", {"form": form})





@login_required
@user_passes_test(lambda u: u.role == "Seller")
def manage_categories(request):
    query = request.GET.get("q")
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)
    return render(request, "manage_categories.html", {"categories": categories})








@login_required
@user_passes_test(lambda u: u.role == "Seller")
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("manage_categories")
    else:
        form = CategoryForm()
    return render(request, "add_category.html", {"form": form})






@login_required
@user_passes_test(lambda u: u.role == "Seller")
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("manage_categories")
    else:
        form = CategoryForm(instance=category)

    return render(request, "edit_category.html", {"form": form, "category": category})






@login_required
@user_passes_test(lambda u: u.role == "Seller")
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect("manage_categories")

    return render(request, "confirm_delete_category.html", {"category": category})





@login_required
@user_passes_test(lambda u: u.role == "Seller")
def manage_suppliers(request):
    query = request.GET.get("q")
    suppliers = Supplier.objects.all()
    if query:
        suppliers = suppliers.filter(name__icontains=query)
    return render(request, "manage_suppliers.html", {"suppliers": suppliers})


@login_required
@user_passes_test(lambda u: u.role == "Seller")
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect("manage_suppliers")
    else:
        form = SupplierForm()
    return render(request, "add_supplier.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.role == "Seller")
def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated.")
            return redirect("manage_suppliers")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "edit_supplier.html", {"form": form, "supplier": supplier})


@login_required
@user_passes_test(lambda u: u.role == "Seller")
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == "POST":
        supplier.delete()
        messages.success(request, "Supplier deleted.")
        return redirect("manage_suppliers")
    return render(request, "confirm_delete_supplier.html", {"supplier": supplier})
















from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Product, Order

@login_required
@user_passes_test(lambda u: u.role == "Seller")
def seller_stats_dashboard(request):
    seller = request.user

    total_orders = Order.objects.filter(user=seller).count()
    total_sales = Order.objects.filter(user=seller, order_status="Completed").count()

    total_revenue = Order.objects.filter(
        user=seller,
        payment_status="Paid"
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    low_stock = Product.objects.filter(seller=seller, stock_quantity__lt=10).count()

    expired_products = Product.objects.filter(
        seller=seller,
        expiry_date__lt=timezone.now().date()
    ).count()

    recent_orders = Order.objects.filter(user=seller).order_by("-order_date")[:10]

    return render(request, "seller_stats_dashboard.html", {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "low_stock": low_stock,
        "expired_products": expired_products,
        "recent_orders": recent_orders,
    })





@login_required
@user_passes_test(lambda u: u.role == "Seller")
def expired_products_list(request):
    seller = request.user
    products = Product.objects.filter(
        seller=seller,
        expiry_date__lt=timezone.now().date()
    ).order_by("expiry_date")
    return render(request, "expired_products_list.html", {"products": products})




@login_required
@user_passes_test(lambda u: u.role == "Seller")
def low_stock_products_list(request):
    seller = request.user
    products = Product.objects.filter(seller=seller, stock_quantity__lt=10).order_by("stock_quantity")
    return render(request, "low_stock_products_list.html", {"products": products})




@login_required
@user_passes_test(lambda u: u.role == "Seller")
def product_performance_report(request):
    seller = request.user
    reports = ProductPerformanceReport.objects.filter(product__seller=seller).order_by("-report_date", "-total_sales")
    return render(request, "product_performance_report.html", {"reports": reports})




@login_required
@user_passes_test(lambda u: u.role == "Seller")
def add_product_performance_report(request):
    seller = request.user
    products = Product.objects.filter(seller=seller)

    if request.method == "POST":
        report_date = request.POST.get("report_date")
        product_id = request.POST.get("product")
        total_sales = request.POST.get("total_sales")
        total_quantity_sold = request.POST.get("total_quantity_sold")
        average_rating = request.POST.get("average_rating")

        product = Product.objects.get(id=product_id, seller=seller)

        ProductPerformanceReport.objects.create(
            report_date=report_date,
            product=product,
            total_sales=total_sales,
            total_quantity_sold=total_quantity_sold,
            average_rating=average_rating
        )

        messages.success(request, "Product performance report added successfully.")
        return redirect("product_performance_report")

    context = {
        "seller_products": products,
        "today": timezone.now().date(),
    }
    return render(request, "add_product_performance.html", context)
















from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shipment
from .forms import ShipmentForm

@login_required
def shipment_list(request):
    shipments = Shipment.objects.all().order_by("-estimated_delivery_date")
    return render(request, "shipment_list.html", {"shipments": shipments})

@login_required
def create_shipment(request):
    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Shipment created successfully.")
            return redirect("shipment_list")
    else:
        form = ShipmentForm()
    return render(request, "shipment_form.html", {"form": form, "title": "Create Shipment"})

@login_required
def edit_shipment(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if request.method == "POST":
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            messages.success(request, "Shipment updated successfully.")
            return redirect("shipment_list")
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, "shipment_form.html", {"form": form, "title": "Edit Shipment"})

@login_required
def delete_shipment(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    shipment.delete()
    messages.success(request, "Shipment deleted successfully.")
    return redirect("shipment_list")




from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "product_detail.html", {"product": product})









@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)

    if created:
        cart_item.quantity = 1  # ✅ Prevent quantity=null
    else:
        cart_item.quantity += 1

    cart_item.save()
    return redirect("cart_view")









@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.quantity * item.product.price for item in cart_items)
    return render(request, "cart_view.html", {
        "cart_items": cart_items,
        "subtotal": subtotal
    })

@login_required
def update_cart_item(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if request.method == "POST":
        try:
            new_qty = int(request.POST.get("quantity", 1))
            cart_item.quantity = max(1, new_qty)
            cart_item.save()
        except:
            pass
    return redirect("cart_view")

@login_required
def remove_cart_item(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect("cart_view")



@login_required
def increase_cart_item(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart_view")

@login_required
def decrease_cart_item(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect("cart_view")






from .models import Order, OrderItem

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by("-order_date")
    return render(request, "orders.html", {"orders": user_orders})













# from django.contrib import messages
# from .models import Cart, Order, OrderItem

# @login_required
# def add_order(request):
#     user = request.user

#     # 🛒 Get cart items for this user
#     cart_items = Cart.objects.filter(user=user)
#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty.")
#         return redirect("cart_view")

#     # 💵 Calculate subtotal
#     subtotal = sum(item.product.price * item.quantity for item in cart_items)

#     # 🧾 Create the order
#     order = Order.objects.create(
#         user=user,
#         total_amount=subtotal,
#         order_status="Pending",
#         payment_status="Pending"
#     )

#     # 📦 Create order items from the cart
#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )

#     # 🧹 Clear the cart
#     cart_items.delete()

#     messages.success(request, f"Order #{order.id} created successfully.")
#     return redirect("orders")




from django.contrib import messages
from .models import Cart, Order
from .utils import transfer_cart_to_order  # ✅ add this

@login_required
def add_order(request):
    user = request.user

    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart_view")

    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        user=user,
        total_amount=subtotal,
        order_status="Pending",
        payment_status="Pending"
    )

    transfer_cart_to_order(user, order)  # ✅ clean and shared

    messages.success(request, f"Order #{order.id} created successfully.")
    return redirect("orders")









from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def manage_account(request):
    user = request.user
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")

        # Update basic fields
        user.first_name = name.split()[0]
        user.last_name = " ".join(name.split()[1:])
        user.email = email
        user.save()

        # Optional: update phone number if stored in profile model
        if hasattr(user, "profile"):
            user.profile.phone = phone
            user.profile.save()

        messages.success(request, "Account details updated successfully.")
        return redirect("manage_account")

    return render(request, "manage_account.html")





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal
    })










# import stripe
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect, render
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# from django.db import transaction
# from .models import Cart, Order, Payment, User

# stripe.api_key = settings.STRIPE_SECRET_KEY

# @login_required
# def create_stripe_session(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     line_items = []

#     for item in cart_items:
#         line_items.append({
#             "price_data": {
#                 "currency": "usd",
#                 "product_data": {"name": item.product.name},
#                 "unit_amount": int(item.product.price * 100),
#             },
#             "quantity": item.quantity,
#         })

#     # Step 1: Create order with pending status
#     order = Order.objects.create(
#         user=request.user,
#         total_amount=sum(item.product.price * item.quantity for item in cart_items),
#         order_status="Pending",
#         payment_status="Pending"
#     )

#     # Step 2: Create Stripe checkout session with metadata
#     session = stripe.checkout.Session.create(
#         payment_method_types=["card"],
#         line_items=line_items,
#         mode="payment",
#         success_url=request.build_absolute_uri("/customer/checkout-success/"),
#         cancel_url=request.build_absolute_uri("/customer/cart/"),
#         metadata={
#             "order_id": str(order.id),
#             "user_id": str(request.user.id)
#         }
#     )

#     return redirect(session.url)


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
#     endpoint_secret = endpoint_secret = "whsec_da0622d0ee1adda88923db76c59bf66f4dbe0f90f8e45908f6a4c2e36cd7d112"

#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except (ValueError, stripe.error.SignatureVerificationError):
#         return HttpResponse(status=400)

#     if event["type"] == "checkout.session.completed":
#         session = event["data"]["object"]
#         order_id = session.get("metadata", {}).get("order_id")
#         user_id = session.get("metadata", {}).get("user_id")

#         try:
#             order = Order.objects.get(id=order_id)
#             user = User.objects.get(id=user_id)

#             # ✅ CREATE and SAVE the Payment (to trigger stock update logic)
#             payment = Payment(
#                 order=order,
#                 user=user,
#                 payment_method="Credit Card",
#                 payment_status="Completed"
#             )
#             payment.save()

#             # ✅ Then update order status
#             order.payment_status = "Paid"
#             order.order_status = "Approved"
#             order.save()

#         except (Order.DoesNotExist, User.DoesNotExist):
#             return HttpResponse(status=404)

#     return HttpResponse(status=200)


# @login_required
# def checkout_success(request):
#     return render(request, "checkout_success.html")





import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction
from .models import Cart, Order, Payment, User
from .utils import transfer_cart_to_order  # ✅ Make sure utils.py exists

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_stripe_session(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect("cart_view")

    line_items = []
    for item in cart_items:
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": item.product.name},
                "unit_amount": int(item.product.price * 100),
            },
            "quantity": item.quantity,
        })

    # ✅ Step 1: Create the Order
    order = Order.objects.create(
        user=request.user,
        total_amount=sum(item.product.price * item.quantity for item in cart_items),
        order_status="Pending",
        payment_status="Pending"
    )

    # ✅ Step 2: Move cart items into OrderItem table
    transfer_cart_to_order(request.user, order)

    # ✅ Step 3: Create Stripe session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=request.build_absolute_uri("/customer/checkout-success/"),
        cancel_url=request.build_absolute_uri("/customer/cart/"),
        metadata={
            "order_id": str(order.id),
            "user_id": str(request.user.id)
        }
    )

    return redirect(session.url)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = "whsec_da0622d0ee1adda88923db76c59bf66f4dbe0f90f8e45908f6a4c2e36cd7d112"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        user_id = session.get("metadata", {}).get("user_id")

        try:
            order = Order.objects.get(id=order_id)
            user = User.objects.get(id=user_id)

            # ✅ Step 4: Register payment and trigger stock logic
            if not order.orderitem_set.exists():
                return HttpResponse("Order has no items.", status=400)

            payment = Payment.objects.create(
                order=order,
                user=user,
                payment_method="Credit Card",
                payment_status="Completed"
            )

            order.payment_status = "Paid"
            order.order_status = "Approved"
            order.save()

        except (Order.DoesNotExist, User.DoesNotExist):
            return HttpResponse(status=404)

    return HttpResponse(status=200)

@login_required
def checkout_success(request):
    return render(request, "checkout_success.html")











from django.contrib.auth import views as auth_views



from .models import Order  # adjust the import based on your app









def pending_orders(request):
    pending_orders = Order.objects.filter(order_status="Pending").select_related("user").prefetch_related("orderitem_set", "payment_set").order_by('-order_date')
    context = {'pending_orders': pending_orders}
    return render(request, "pending_orders.html", context)





from django.shortcuts import redirect, get_object_or_404
from .models import Order

def approve_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.order_status = "Approved"
    order.save()
    return redirect("pending_orders")

def reject_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.order_status = "Rejected"
    order.save()
    return redirect("pending_orders")






from .models import Order

def seller_all_orders_view(request):
    orders = Order.objects.select_related("user").order_by("-order_date")
    return render(request, "seller_all_orders.html", {"orders": orders})





from django.db.models import Sum
from .models import Order, OrderItem

def view_sales(request):
    # Get only paid orders
    sales = Order.objects.filter(payment_status="Paid").select_related("user").order_by("-order_date")
    total_sales = sales.aggregate(total=Sum("total_amount"))["total"] or 0

    # Analytics: group by product
    product_sales = (
        OrderItem.objects
        .filter(order__payment_status="Paid", product__seller=request.user)
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")
    )

    chart_labels = [item["product__name"] for item in product_sales]
    chart_data = [item["total_sold"] for item in product_sales]

    return render(request, "view_sales.html", {
        "sales": sales,
        "total_sales": total_sales,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    })




from django.db.models import Sum
from .models import OrderItem

def sales_analytics(request):
    product_sales = (
        OrderItem.objects
        .values("product__name")
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")
    )

    labels = [item["product__name"] for item in product_sales]
    data = [item["total_sold"] for item in product_sales]

    return render(request, "sales_analytics.html", {
        "labels": labels,
        "data": data
    })





from .models import Shipment
from django.contrib.auth.decorators import login_required

@login_required
def customer_shipments_view(request):
    shipments = Shipment.objects.filter(order__user=request.user).select_related("order")
    return render(request, "customer_shipments.html", {"shipments": shipments})





from django.db.models import Sum, F, Q, ExpressionWrapper, DecimalField, IntegerField, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Product

@login_required
@user_passes_test(lambda u: u.role == "Seller")
def stock_overview(request):
    seller = request.user

    products = Product.objects.filter(seller=seller).annotate(
        sold=Sum(
            'orderitem__quantity',
            filter=Q(orderitem__order__payment_status='Paid')
        ),
        profit=Sum(
            ExpressionWrapper(
                (F('price') - F('cost')) * F('orderitem__quantity'),
                output_field=DecimalField()
            ),
            filter=Q(orderitem__order__payment_status='Paid')
        ),
        remaining_stock=ExpressionWrapper(
            F('stock_quantity') - Coalesce(
                Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid')),
                Value(0, output_field=IntegerField())
            ),
            output_field=IntegerField()
        )
    )

    total_profit = sum((p.profit or 0) for p in products)

    return render(request, "stock.html", {
        "product_data": products,
        "total_profit": total_profit,
    })











# from django.shortcuts import get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.db.models import F
# from .models import Order

# @login_required
# @user_passes_test(lambda u: u.role == "Seller" or u.is_staff)
# def mark_order_paid(request, order_id):
#     order = get_object_or_404(Order, id=order_id)

#     if order.payment_status != "Paid":
#         order.payment_status = "Paid"
#         order.save()

#         for item in order.orderitem_set.all():
#             product = item.product
#             product.stock_quantity = F("stock_quantity") - item.quantity
#             product.save()
#             product.refresh_from_db()  # ensures correct value is reflected later

#     return redirect("seller_all_orders")


























# part of clean

# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.db.models import Sum, Q
# from .models import Order, Product, OrderItem

# # Seller audit dashboard: unpaid orders missing items + unsold products
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def audit_missing_orderitems(request):
#     # Find this seller's paid orders with no OrderItems
#     empty_paid_orders = Order.objects.filter(
#         payment_status='Paid',
#         user=request.user,
#         orderitem__isnull=True
#     ).distinct()

#     # Find this seller's products that have never been sold in any paid order
#     unsold_products = Product.objects.filter(seller=request.user).annotate(
#         total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid'))
#     ).filter(total_sold__isnull=True)

#     return render(request, 'audit_report.html', {
#         "empty_paid_orders": empty_paid_orders,
#         "unsold_products": unsold_products,
#     })



# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from .models import Order, OrderItem, Product

# def fix_order_items(request, order_id):
#     order = get_object_or_404(Order, pk=order_id, payment_status='Paid')

#     # Find missing products for this order
#     missing_products = Product.objects.filter(seller=order.user, stock_quantity__gt=0)[:2]

#     if not missing_products:
#         messages.warning(request, f"No available stock to fix Order #{order.id}.")
#     else:
#         for product in missing_products:
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=1,
#                 price=product.price
#             )
#             # Deduct stock
#             product.stock_quantity -= 1
#             product.save()

#         messages.success(request, f"Fixed Order #{order.id} with {len(missing_products)} item(s).")

#     return redirect('audit_missing_orders')






# def update_profit():
#     products = Product.objects.all()
#     total_profit = 0

#     for product in products:
#         sold_quantity = OrderItem.objects.filter(product=product, order__payment_status='Paid').count()
#         product.sold_quantity = sold_quantity
#         product.remaining_stock = product.original_quantity - sold_quantity
#         product.total_profit = sold_quantity * (product.price - product.cost)
#         product.save()

#         total_profit += product.total_profit

#     return total_profit









# # Attach an unsold product to a paid order by same seller
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_unsold_product(request, product_id):
#     product = get_object_or_404(Product, pk=product_id, seller=request.user)

#     # Find a paid order belonging to the same seller/user
#     paid_order = Order.objects.filter(payment_status='Paid', user=request.user).exclude(
#         orderitem__product=product
#     ).first()

#     if not paid_order:
#         messages.warning(request, f"No available paid order found to link {product.name}.")
#     else:
#         OrderItem.objects.create(
#             order=paid_order,
#             product=product,
#             quantity=1,
#             price=product.price
#         )
#         messages.success(request, f"{product.name} added to Order #{paid_order.id} with quantity 1.")

#     return redirect('audit_missing_orderitems')



# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_all_missing_orders(request):
#     if request.method == "POST":
#         orders = Order.objects.filter(payment_status='Paid', user=request.user).distinct()
#         products = Product.objects.filter(seller=request.user)
#         fixed_count = 0

#         for order in orders:
#             for product in products:
#                 if not OrderItem.objects.filter(order=order, product=product).exists():
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         quantity=1,
#                         price=product.price
#                     )
#                     fixed_count += 1

#         messages.success(request, f"✅ Fixed {fixed_count} missing item(s) across all paid orders.")

#     # ✅ Use the correct route name here to avoid NoReverseMatch
#     return redirect('audit_missing_orders')





# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_all_unsold_products(request):
#     if request.method == "POST":
#         unsold_products = Product.objects.filter(seller=request.user).annotate(
#             total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid'))
#         ).filter(total_sold__isnull=True)

#         paid_order = Order.objects.filter(payment_status='Paid', user=request.user).first()

#         if paid_order:
#             for product in unsold_products:
#                 OrderItem.objects.get_or_create(
#                     order=paid_order,
#                     product=product,
#                     defaults={
#                         'quantity': 1,
#                         'price': product.price
#                     }
#                 )
#             messages.success(
#                 request,
#                 f"✅ Registered {unsold_products.count()} unsold product(s) in Order #{paid_order.id}."
#             )
#         else:
#             messages.warning(request, "No paid order found for this seller.")

#     # ✅ Route name now matches your URL config
#     return redirect('audit_missing_orders')
























# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.db.models import Sum, Q
# from .models import Order, Product, OrderItem

# # AUDIT DASHBOARD
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def audit_missing_orders(request):
#     empty_paid_orders = Order.objects.filter(
#         payment_status='Paid',
#         user=request.user,
#         orderitem__isnull=True
#     ).distinct()

#     unsold_products = Product.objects.filter(seller=request.user).annotate(
#         total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid'))
#     ).filter(total_sold__isnull=True)

#     return render(request, 'audit_report.html', {
#         "empty_paid_orders": empty_paid_orders,
#         "unsold_products": unsold_products,
#     })

# # FIX INDIVIDUAL ORDER
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_order_items(request, order_id):
#     order = get_object_or_404(Order, pk=order_id, payment_status='Paid', user=request.user)
#     if OrderItem.objects.filter(order=order).exists():
#         messages.info(request, f"Order #{order.id} already has items.")
#     else:
#         products = Product.objects.filter(seller=request.user)[:2]
#         for product in products:
#             OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
#         messages.success(request, f"Fixed Order #{order.id} with {len(products)} item(s).")
#     return redirect('audit_missing_orders')

# # FIX INDIVIDUAL PRODUCT
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_unsold_product(request, product_id):
#     product = get_object_or_404(Product, pk=product_id, seller=request.user)
#     paid_order = Order.objects.filter(payment_status='Paid', user=request.user).exclude(
#         orderitem__product=product
#     ).first()
#     if not paid_order:
#         messages.warning(request, f"No paid order found to link {product.name}.")
#     else:
#         OrderItem.objects.create(order=paid_order, product=product, quantity=1, price=product.price)
#         messages.success(request, f"{product.name} added to Order #{paid_order.id}.")
#     return redirect('audit_missing_orders')

# # FIX ALL ORDERS
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_all_missing_orders(request):
#     if request.method == "POST":
#         orders = Order.objects.filter(payment_status='Paid', user=request.user)
#         products = Product.objects.filter(seller=request.user)
#         fixed = 0
#         for order in orders:
#             for product in products:
#                 if not OrderItem.objects.filter(order=order, product=product).exists():
#                     OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
#                     fixed += 1
#         messages.success(request, f"✅ Fixed {fixed} missing item(s) across all paid orders.")
#     return redirect('audit_missing_orders')

# # FIX ALL UNSOLD PRODUCTS
# @login_required
# @user_passes_test(lambda u: u.role == "Seller")
# def fix_all_unsold_products(request):
#     if request.method == "POST":
#         unsold = Product.objects.filter(seller=request.user).annotate(
#             total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid'))
#         ).filter(total_sold__isnull=True)
#         paid_order = Order.objects.filter(payment_status='Paid', user=request.user).first()
#         created = 0
#         if paid_order:
#             for product in unsold:
#                 item, was_created = OrderItem.objects.get_or_create(
#                     order=paid_order,
#                     product=product,
#                     defaults={'quantity': 1, 'price': product.price}
#                 )
#                 if was_created:
#                     created += 1
#             messages.success(request, f"✅ Registered {created} unsold product(s) in Order #{paid_order.id}.")
#         else:
#             messages.warning(request, "No paid order found for this seller.")
#     return redirect('audit_missing_orders')



from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import render
from .models import Order, OrderItem, Product

@login_required
@user_passes_test(lambda u: u.role == "Seller")
def customer_info_view(request):
    seller = request.user
    search_term = request.GET.get("search", "").strip().lower()

    orders = (
        Order.objects.filter(orderitem__product__seller=seller)
        .select_related("user")
        .prefetch_related("orderitem_set__product")
        .distinct()
    )

    customer_data = []
    total_money = 0

    for order in orders:
        user = order.user
        full_name = user.get_full_name().strip() or user.username

        # Apply search filter
        if search_term and search_term not in full_name.lower():
            continue

        order_items = order.orderitem_set.filter(product__seller=seller)

        product_names = ", ".join(item.product.name for item in order_items)
        total_quantity = order_items.aggregate(q=Sum("quantity"))["q"] or 0
        order_total = sum(item.quantity * item.price for item in order_items)

        phone = getattr(user, "phone", "N/A")
        address = getattr(user, "address", "N/A")

        total_money += order_total

        customer_data.append({
            "name": full_name,
            "email": user.email,
            "phone": phone,
            "address": address,
            "products": product_names,
            "order_id": order.id,
            "total_quantity": total_quantity,
            "payment_status": order.payment_status,
            "order_date": order.order_date,
            "total_amount": order_total,
        })

    return render(request, "customer_info.html", {
        "customer_data": customer_data,
        "total_money": total_money
    })








from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order

@login_required
@user_passes_test(lambda u: u.role == "Seller")
def generate_customer_report(request, order_id):
    order = (
        Order.objects.filter(id=order_id, orderitem__product__seller=request.user)
        .distinct()
        .first()
    )
    if not order:
        raise Http404("No matching order found.")

    items = order.orderitem_set.filter(product__seller=request.user)

    report_items = []
    grand_total = 0

    for item in items:
        line_total = item.quantity * item.price
        grand_total += line_total
        report_items.append({
            "product": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
            "total": line_total,
        })

    html = render_to_string("customer_report.html", {
        "order": order,
        "items": report_items,
        "grand_total": grand_total,
        "seller": request.user,
        "customer_name": order.user.get_full_name() or order.user.username,
        "email": order.user.email,
        "phone": getattr(order.user, "phone", "N/A"),
        "address": getattr(order.user, "address", "N/A"),
    })

    return HttpResponse(html)









from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from .models import Shipment

@login_required
@user_passes_test(lambda u: u.role == "Seller")
def shipment_report(request, shipment_id):
    shipment = (
        Shipment.objects.filter(id=shipment_id, order__orderitem__product__seller=request.user)
        .select_related("order__user")
        .first()
    )
    if not shipment:
        raise Http404("Shipment not found.")

    customer = shipment.order.user

    html = render_to_string("shipment_report.html", {
        "shipment": shipment,
        "customer": customer,
        "seller": request.user,
    })

    return HttpResponse(html)









    

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from .models import Order

@login_required
@user_passes_test(lambda u: u.role == "Seller" or u.is_staff)
def mark_order_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.payment_status != "Paid":
        order.payment_status = "Paid"
        order.save()

        for item in order.orderitem_set.all():
            product = item.product
            product.stock_quantity = F("stock_quantity") - item.quantity
            product.save()
            product.refresh_from_db()  # ensures correct value is reflected later

    return redirect("seller_all_orders")







from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, date
from .models import OrderItem, Product

@login_required
@user_passes_test(lambda u: hasattr(u, "role") and u.role == "Seller")
def sales_analytics(request):
    seller = request.user

    # Parse start and end date from query
    start_str = request.GET.get("start_date")
    end_str = request.GET.get("end_date")

    today = date.today()
    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else today
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else today
    except ValueError:
        start_date = end_date = today

    # Filter OrderItems from this seller's products within the selected date range
    items = OrderItem.objects.filter(
        product__seller=seller,
        order__order_date__date__range=(start_date, end_date)
    )

    sales_by_product = {}
    revenue_by_product = {}

    for item in items:
        name = item.product.name
        qty = item.quantity
        revenue = float(item.price) * qty

        sales_by_product[name] = sales_by_product.get(name, 0) + qty
        revenue_by_product[name] = revenue_by_product.get(name, 0) + revenue

    # Prepare chart and summary context
    context = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_revenue": sum(revenue_by_product.values()),
        "order_labels": list(sales_by_product.keys()),
        "order_counts": list(sales_by_product.values()),
        "category_labels": list(revenue_by_product.keys()),
        "category_sales": list(revenue_by_product.values()),
        "dates": [f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"],
        "sales_data": [sum(revenue_by_product.values())],
        "top_products": [
            {"name": k, "total_sold": v}
            for k, v in sorted(sales_by_product.items(), key=lambda x: x[1], reverse=True)[:5]
        ],
    }

    return render(request, "sales_analytics.html", context)






from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, date
from .models import OrderItem

@login_required
def print_sales_report(request):
    seller = request.user
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date() if start else date.today()
        end_date = datetime.strptime(end, "%Y-%m-%d").date() if end else date.today()
    except ValueError:
        start_date = end_date = date.today()

    # Filter order items by seller and date range
    items = OrderItem.objects.filter(
        product__seller=seller,
        order__order_date__date__range=(start_date, end_date)
    )

    # Aggregate sales and revenue per product
    summary = {}
    for item in items:
        name = item.product.name
        qty = item.quantity
        revenue = float(item.price) * qty
        if name in summary:
            summary[name]['qty'] += qty
            summary[name]['revenue'] += revenue
        else:
            summary[name] = {'qty': qty, 'revenue': revenue}

    # Prepare chart data
    product_names = list(summary.keys())
    revenue_values = [round(val['revenue'], 2) for val in summary.values()]
    quantity_values = [val['qty'] for val in summary.values()]

    context = {
        "seller": seller,
        "start_date": start_date,
        "end_date": end_date,
        "products": summary,
        "total": sum(revenue_values),
        "product_names": product_names,
        "revenue_values": revenue_values,
        "quantity_values": quantity_values,
    }

    return render(request, "print_sales_report.html", context)








import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Product, Cart
from django.contrib.auth.decorators import login_required

@csrf_exempt
@login_required
def sync_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("items", [])

            for pid in product_ids:
                try:
                    product = Product.objects.get(id=pid)
                    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
                    if created:
                        cart_item.quantity = 1
                    else:
                        cart_item.quantity += 1
                    cart_item.save()
                except Product.DoesNotExist:
                    continue

            return JsonResponse({"success": True})
        except:
            return JsonResponse({"success": False}, status=400)
    return JsonResponse({"success": False}, status=405)





    from django.shortcuts import render

def services_page(request):
    return render(request, "services.html")