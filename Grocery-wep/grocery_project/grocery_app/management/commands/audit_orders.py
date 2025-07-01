from django.core.management.base import BaseCommand
from grocery_app.models import Order, Product
from django.db.models import Sum, Q

class Command(BaseCommand):
    help = "Audit paid orders missing OrderItems and products with no sales"

    def handle(self, *args, **kwargs):
        self.stdout.write("Verifying paid orders...\n")

        paid_orders = Order.objects.filter(payment_status="Paid")
        missing_items = paid_orders.filter(orderitem__isnull=True)

        if missing_items.exists():
            self.stdout.write("Paid orders without any OrderItems:")
            for order in missing_items:
                self.stdout.write(f" - Order #{order.id} | User: {order.user.username} | Total: ${order.total_amount}")
        else:
            self.stdout.write("All paid orders have associated items.")

        self.stdout.write("\nChecking for products never sold in any paid order:")
        unsold_products = Product.objects.annotate(
            sold=Sum("orderitem__quantity", filter=Q(orderitem__order__payment_status="Paid"))
        ).filter(sold__isnull=True)

        if unsold_products.exists():
            for product in unsold_products:
                seller = product.seller.username if product.seller else "None"
                self.stdout.write(f" - {product.name} | Seller: {seller} | Stock: {product.stock_quantity}")
        else:
            self.stdout.write("All products have been sold in at least one paid order.")