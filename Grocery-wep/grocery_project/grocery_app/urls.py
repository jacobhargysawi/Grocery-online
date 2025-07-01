from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    home, base, register, login_view, logout_view, about, contact,
    admin_login, customer_login, admin_dashboard, customer_dashboard, register_seller, login_seller,
    seller_dashboard, logout_seller, reset_seller_password, pending_orders, view_sales, shipment,
    customer_register, customer_login, reset_customer_password, browse_products, cart_view, orders,
    checkout, manage_account, track_shipment  , customer_master , customer_logout

    , add_to_cart  , manage_products   , update_product, delete_product  , add_product 

    ,  manage_categories     ,  add_category  ,  update_category , delete_category

    , manage_suppliers, add_supplier, update_supplier, delete_supplier

    , seller_stats_dashboard   , expired_products_list , low_stock_products_list

    , product_performance_report  ,  add_product_performance_report  

     ,   shipment_list, create_shipment, edit_shipment, delete_shipment , product_detail

     , update_cart_item  ,  remove_cart_item  , increase_cart_item, decrease_cart_item


     , add_order , create_stripe_session   

     ,  stripe_webhook  , checkout_success  ,  approve_order   , reject_order  ,  seller_all_orders_view
  
   , sales_analytics  ,  customer_shipments_view   , stock_overview  , customer_info_view ,  generate_customer_report
   
   ,   shipment_report , mark_order_paid     ,   view_contact_messages , delete_contact_message

   , print_sales_report  , sync_cart , services_page
)

urlpatterns = [
    # 🔹 Base & Static Pages
    path("", base, name="base"),
    path("home/", home, name="home"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),

    # 🔹 Pending & Shipment Management
    path("pending-orders/", pending_orders, name="pending_orders"),
    path("view-sales/", view_sales, name="view_sales"),
    path("shipments/", shipment, name="shipment"),

    # 🔹 Authentication Routes
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # 🔹 Admin, Seller & Customer Login Routes
    path("admin/login/", admin_login, name="admin_login"),
    path("seller/login/", login_seller, name="seller_login"),
    path("customer/login/", customer_login, name="customer_login"),

    # 🔹 Role-Based Dashboards
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("seller/dashboard/", seller_dashboard, name="seller_dashboard"),
    path("customer/dashboard/", customer_dashboard, name="customer_dashboard"),  # ✅ Ensure customer_master.html exists

    # 🔹 Seller Management
    path("seller/register/", register_seller, name="register_seller"),
    path("seller/logout/", logout_seller, name="seller_logout"),
    path("seller/reset-password/", reset_seller_password, name="reset_seller_password"),

    # 🔹 Customer Management
    path("customer/register/", customer_register, name="customer_register"),
    path("customer/login/", customer_login, name="customer_login"),
    path("customer/reset-password/", reset_customer_password, name="reset_customer_password"),

    # 🔹 Customer Panel Features (Ensure Templates Exist)
    path("customer/browse-products/", browse_products, name="browse_products"),
    path("customer/cart/", cart_view, name="cart_view"),
    path("customer/orders/", orders, name="orders"),
    path("customer/checkout/", checkout, name="checkout"),
    path("customer/manage-account/", manage_account, name="manage_account"),
    path("customer/track-shipment/", track_shipment, name="track_shipment"),
    path("customer/master/", customer_master, name="customer_master"),
    path("customer/logout/", customer_logout, name="customer_logout"),  # ✅ Ensure this pattern exists
    path("customer/browse-products/", browse_products, name="browse_products"),
    path("customer/cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),  # ✅ Ensure this pattern exists

    path("seller/products/", manage_products, name="manage_products"),

    path("seller/products/edit/<int:product_id>/", update_product, name="update_product"),
    path("seller/products/delete/<int:product_id>/", delete_product, name="delete_product"),
    path("seller/products/add/", add_product, name="add_product"),
    path("seller/categories/", manage_categories, name="manage_categories"),
    path("seller/categories/add/", add_category, name="add_category"),
    path("seller/categories/edit/<int:category_id>/", update_category, name="update_category"),
    path("seller/categories/delete/<int:category_id>/", delete_category, name="delete_category"),

    path("seller/suppliers/", manage_suppliers, name="manage_suppliers"),
    path("seller/suppliers/add/", add_supplier, name="add_supplier"),
    path("seller/suppliers/edit/<int:supplier_id>/", update_supplier, name="update_supplier"),
    path("seller/suppliers/delete/<int:supplier_id>/", delete_supplier, name="delete_supplier"),

    path("seller/dashboard/stats/", seller_stats_dashboard, name="seller_stats_dashboard"),

    path("seller/expired-products/", expired_products_list, name="expired_products_list"),

    path("seller/low-stock-products/", low_stock_products_list, name="low_stock_products_list"),

    path("seller/performance-report/", product_performance_report, name="product_performance_report"),

    path(
        "seller/performance-report/add/",
        add_product_performance_report,
        name="add_product_performance"
    ),




   path("seller/shipments/", shipment_list, name="shipment_list"),

    # 🔹 Create New Shipment
    path("seller/shipments/create/", create_shipment, name="create_shipment"),

    # 🔹 Edit a Shipment
    path("seller/shipments/<int:id>/edit/", edit_shipment, name="edit_shipment"),

    # 🔹 Delete a Shipment
    path("seller/shipments/<int:id>/delete/", delete_shipment, name="delete_shipment"),

    path("customer/product/<int:id>/", product_detail, name="product_detail"),


    path("customer/cart/", cart_view, name="cart_view"),
    path("customer/cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("customer/cart/update/<int:cart_id>/", update_cart_item, name="update_cart_item"),
    path("customer/cart/remove/<int:cart_id>/", remove_cart_item, name="remove_cart_item"),

    # 🔹 Quantity Controls
    path("customer/cart/increase/<int:cart_id>/", increase_cart_item, name="increase_cart_item"),
    path("customer/cart/decrease/<int:cart_id>/", decrease_cart_item, name="decrease_cart_item"),
    path("customer/orders/", orders, name="orders"),

    path("customer/orders/add/", add_order, name="add_order"),
    path("customer/manage-account/", manage_account, name="manage_account"),

    
    path("customer/checkout/", checkout, name="checkout"),
    path("customer/create-stripe-session/", create_stripe_session, name="create_stripe_session"),




    # 🔁 Stripe Webhook Endpoint
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),


    path("customer/checkout-success/", checkout_success, name="checkout_success"),





    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='reset_customer_password.html'), name='reset_password'),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_password_form.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),





   path("seller/orders/<int:order_id>/approve/", approve_order, name="approve_order"),
   path("seller/orders/<int:order_id>/reject/", reject_order, name="reject_order"),

   path("seller/orders/", seller_all_orders_view, name="seller_all_orders"),


   path("seller/analytics/", sales_analytics, name="sales_analytics"),

   path("customer/shipments/", customer_shipments_view, name="customer_shipments"),

   path("seller/stock/", stock_overview, name="stock_overview"),

#    path("orders/<int:order_id>/mark-paid/", mark_order_paid, name="mark_order_paid"),



path("seller/customers/", customer_info_view, name="customer_info"),

    path("seller/customer-report/<int:order_id>/", generate_customer_report, name="generate_customer_report"),

path("seller/shipment-report/<int:shipment_id>/", shipment_report, name="shipment_report"),

   path("orders/<int:order_id>/mark-paid/", mark_order_paid, name="mark_order_paid"),

       path('contact/messages/', view_contact_messages, name='view_contact_messages'),
           path('contact/delete/<int:pk>/', delete_contact_message, name='delete_contact_message'),


path('seller/analytics/report/', print_sales_report, name='print_sales_report'),

path("cart/sync/", sync_cart, name="sync_cart"),

path('services/', services_page, name='services')

]



