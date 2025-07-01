from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Category, Supplier, Product, Order, OrderItem, Payment,
    Cart, Review, Shipment, SalesReport, InventoryReport,
    CustomerAnalytics, ProductPerformanceReport, EmployeeSalary
)
from .forms import UserRegisterForm, CustomUserChangeForm  # From your forms.py

# ---------------------- USER ADMIN WITH HASHED PASSWORDS ----------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserRegisterForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'role', 'phone', 'created_at')
    search_fields = ('username', 'role', 'phone')
    list_filter = ('role',)

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("role", "phone", "address")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "phone", "address")}),
    )

# ---------------------- ALL OTHER MODELS ----------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_phone', 'contact_email')
    search_fields = ('name', 'contact_phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'seller', 'category')
    list_filter = ('category', 'seller')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_status', 'payment_status', 'order_date')
    list_filter = ('order_status', 'payment_status')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('product__name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'payment_method', 'payment_status', 'transaction_date')
    list_filter = ('payment_status',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    search_fields = ('user__username', 'product__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    list_filter = ('rating',)

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'tracking_number', 'carrier', 'estimated_delivery_date', 'status')
    list_filter = ('status',)
    search_fields = ('tracking_number',)

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'total_sales_amount', 'total_orders', 'total_items_sold', 'report_generated_at')
    search_fields = ('report_date',)

@admin.register(InventoryReport)
class InventoryReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'product', 'current_stock_quantity', 'expiry_date', 'low_stock_level', 'report_generated_at')
    search_fields = ('product__name', 'report_date')

@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_orders', 'total_spent', 'average_order_value', 'last_order_date', 'analytics_generated_at')
    search_fields = ('user__username',)

@admin.register(ProductPerformanceReport)
class ProductPerformanceReportAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'product', 'total_sales', 'total_quantity_sold', 'average_rating')
    search_fields = ('product__name', 'report_date')

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'base_salary', 'bonus', 'total_salary', 'payment_month', 'paid_at')
    search_fields = ('user__username', 'payment_month')
    list_filter = ('payment_month',)
    readonly_fields = ('total_salary', 'paid_at')



from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('sent_at',)