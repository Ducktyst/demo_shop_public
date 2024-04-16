from django.urls import path

from shop.views import ProductView
from shop.views import ProductListView
from shop.views import FindUs
from shop.views import about

urlpatterns = [
    path("about", about, name="about"),
    path("find_us", FindUs.as_view(), name="find_us"),

    path("", ProductListView.as_view(), name="home"),
    path("products", ProductListView.as_view(), name="products"),
    path("products/<int:cat_id>", ProductListView.as_view(), name="products-cat"),
    path("product/<int:pk>", ProductView.as_view(), name="product-detail"),
]
