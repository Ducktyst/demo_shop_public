from django.urls import path

from shop.views import (ProductView,
                        LoginPageView,
                        LogoutPageView,
                        RegisterView,
                        CartDetail,
                        CartProductAdd,
                        CartProductDelete,
                        CartConfirm,
                        OrdersList,
                        OrderDetail,
                        OrderDelete)
from shop.views import ProductListView
from shop.views import FindUs
from shop.views import about

auth_urlpatterns = [
    path('login', LoginPageView.as_view(), name='login-customer'),
    path('logout', LogoutPageView.as_view(), name='logout-customer'),
    path('register', RegisterView.as_view(), name='register-customer'),
]

urlpatterns = [
    path("about", about, name="about"),
    path("find_us", FindUs.as_view(), name="find_us"),

    path("", ProductListView.as_view(), name="home"),
    path("products", ProductListView.as_view(), name="products"),
    path("products/<int:cat_id>", ProductListView.as_view(), name="products-cat"),
    path("product/<int:pk>", ProductView.as_view(), name="product-detail"),

    path("cart", CartDetail.as_view(), name="cart"),
    path("cart/add", CartProductAdd.as_view(), name="cart-add-product"),  # ?product_id=<int:pk>
    path("cart/delete", CartProductDelete.as_view(), name="cart-delete-product"),  # ?product_id=<int:pk>
    path("cart/confirm", CartConfirm.as_view(), name="cart-confirm-order"),

    path("orders/", OrdersList.as_view(), name="orders"),
    path("orders/<int:pk>", OrderDetail.as_view(), name="order-get"),
    path("orders/<int:pk>/delete", OrderDelete.as_view(), name="order-delete"),
] + auth_urlpatterns
