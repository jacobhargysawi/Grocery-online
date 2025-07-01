# from .models import Cart, OrderItem

# def transfer_cart_to_order(user, order):
#     cart_items = Cart.objects.filter(user=user)
#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )
#     cart_items.delete()





from .models import Cart, OrderItem

def transfer_cart_to_order(user, order):
    cart_items = Cart.objects.filter(user=user)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    cart_items.delete()