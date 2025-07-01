from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

# ---------------------- CUSTOM USER MODEL ----------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('Customer', 'Customer'),
    ]
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Customer')  
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)

    def __str__(self):
        return self.username

# ---------------------- CATEGORY MODEL ----------------------
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

# ---------------------- SUPPLIER MODEL ----------------------
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# ---------------------- PRODUCT MODEL ----------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Added this
    stock_quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to="images/", null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Seller'})
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Notify seller if stock is low
        if self.stock_quantity < 5:
            print(f"⚠ Warning: Low stock for {self.name}. Seller: {self.seller.username}")

    def __str__(self):
        return self.name






# ---------------------- ORDER MODEL ----------------------
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Customer'})
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'), ('Processing', 'Processing'),
            ('Shipped', 'Shipped'), ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'), ('Approved', 'Approved'), ('Rejected', 'Rejected')
        ],
        default='Pending'
    )
    payment_status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending')

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

# ---------------------- ORDER ITEM MODEL ----------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"





# # ---------------------- PAYMENT MODEL (Updated for Stock Reduction & Transaction Safety) ----------------------
# class Payment(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     payment_method = models.CharField(max_length=100, choices=[
#         ('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Cash on Delivery', 'Cash on Delivery')
#     ])
#     payment_status = models.CharField(max_length=50, choices=[
#         ('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')
#     ], default='Pending')
#     transaction_date = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)  # Save payment first

#         if self.payment_status == "Completed":
#             with transaction.atomic():  # Ensures rollback if stock issue occurs
#                 for item in self.order.orderitem_set.select_related('product'):
#                     if item.product.stock_quantity >= item.quantity:
#                         item.product.stock_quantity -= item.quantity
#                         item.product.save()
#                     else:
#                         raise ValueError(f"🚨 Insufficient stock for {item.product.name}. Available: {item.product.stock_quantity}")

#     def __str__(self):
#         return f"Payment for {self.order.id} - {self.payment_method}"







# ---------------------- PAYMENT MODEL (Preserves Original Stock) ----------------------
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100, choices=[
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('Cash on Delivery', 'Cash on Delivery')
    ])
    payment_status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ], default='Pending')
    transaction_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # ✅ Save the payment record
        super().save(*args, **kwargs)

        # ✅ No longer modify product.stock_quantity here
        # If needed, log or tag transactions separately using signals or reporting models
        # For example: SalesLog.objects.create(...) ← optional

    def __str__(self):
        return f"Payment for Order #{self.order.id} by {self.user.username} via {self.payment_method}"









# ---------------------- SALES REPORT MODEL ----------------------
class SalesReport(models.Model):
    report_date = models.DateField()
    total_sales_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.IntegerField()
    total_items_sold = models.IntegerField()
    report_generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sales Report {self.report_date} - Total Sales: {self.total_sales_amount}"

# ---------------------- INVENTORY REPORT MODEL ----------------------
class InventoryReport(models.Model):
    report_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current_stock_quantity = models.IntegerField()
    expiry_date = models.DateField(null=True, blank=True)
    low_stock_level = models.IntegerField()
    report_generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inventory Report {self.report_date} - {self.product.name} ({self.current_stock_quantity})"

# ---------------------- EMPLOYEE SALARY MODEL ----------------------
class EmployeeSalary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['Admin', 'Seller']})
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_month = models.CharField(max_length=20)  # e.g. "June 2025"
    paid_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_salary = self.base_salary + self.bonus
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.payment_month} - ${self.total_salary}"



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Ensures no NULL values
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Add validation if needed
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.product.name}"
    



class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=255, null=True, blank=True)
    carrier = models.CharField(max_length=100, null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('Processing', 'Processing'), ('Shipped', 'Shipped'),
            ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered')
        ],
        default='Processing'
    )

    def __str__(self):
        return f"Shipment {self.id} - {self.status}"
    





class CustomerAnalytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_orders = models.IntegerField()
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    last_order_date = models.DateTimeField()
    analytics_generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.user.username} - Total Spent: {self.total_spent}"
    



class ProductPerformanceReport(models.Model):
    report_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity_sold = models.IntegerField()
    average_rating = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} Performance - Sales: {self.total_sales}"
    



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)




from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"