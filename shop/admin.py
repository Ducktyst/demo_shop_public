from django.contrib import admin

from shop.models import Product
from shop.models import Category
from shop.models import Cart
from shop.models import CartItem
from shop.models import Order

from shop.models import OrderItem

# Нужно только для отображения в админ-панели
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
