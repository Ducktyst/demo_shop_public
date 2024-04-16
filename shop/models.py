from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

from django.db import models

from demoproject import settings


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    price = models.DecimalField(decimal_places=2, max_digits=7, blank=False)  # 10000.00
    quantity = models.IntegerField(default=0)
    image = models.ImageField(blank=True)
    manufacture_year = models.CharField(max_length=4, validators=[MinLengthValidator(4)], blank=True)
    country = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # вместо удаления

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return f'{self.name} {self.quantity}шт. по {self.price}р.'

    def image_url(self):
        if not self.image:
            return f"{settings.STATIC_URL}images/default_product_img.jpg"

        return self.image.url


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'


class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.IntegerField()

    class Meta:
        verbose_name = 'Товар корзины'
        verbose_name_plural = 'Товары в корзине'

    def __str__(self):
        return f'{self.product.name} x {self.count}шт.'


class Order(models.Model):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    DECLINED = "DECLINED"
    STATUSES = (
        (NEW, "Новый"),  # (Значение, Отображаемое имя)
        (CONFIRMED, "Подтвержден"),
        (DECLINED, "Отклонен"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    status = models.CharField(
        max_length=12,
        choices=STATUSES,
        default=NEW,
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(decimal_places=2, max_digits=7)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.created_at}"

    def status_name(self):
        for status in self.STATUSES:
            if status[0] == self.status:
                return status[1]
        return ''


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.IntegerField()

    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"

    def __str__(self):
        return f"{self.product.name} x {self.count}"
