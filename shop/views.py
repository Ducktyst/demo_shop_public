from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, View, ListView, CreateView
from django.contrib.auth.views import LoginView, LogoutView

from shop.forms import RegisterForm, LoginForm
from shop.mixins import CustomerLoginRequiredMixin
from shop.models import Product, Category, Cart, CartItem


def about(request, *args, **kwargs):
    last_added = Product.objects.order_by('-added_at').all()[:5]  # OFFSET, LIMIT
    context = {"products": last_added}
    return render(request, "about.html", context)


class FindUs(TemplateView):
    template_name = "find_us.html"


class ProductView(DetailView):
    model = Product
    template_name = "catalog/product.html"


class ProductListView(ListView):
    model = Product
    template_name = "catalog/catalog.html"
    paginate_by = 5

    sortings = {
        "added_at": "Сначала старые",
        "-added_at": "Сначала новые",  # убывающий, сначала большие
        "manufacture_year": "Год производства. По возрастанию",
        "-manufacture_year": "Год производства. По убыванию",
        "name": "Наименование. А-Я",
        "-name": "Наименование. Я-А",
        "price": "Цена. По возрастанию",
        "-price": "Цена. По убыванию",
    }
    default_order_by = "-added_at"

    def get_context_data(self, *, object_list=None, **kwargs):

        # print(self.request.GET.urlencode())
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update({
            "curr_order_by": self.request.GET.get("order_by", self.default_order_by),
            "curr_cat_id": self.kwargs.get("cat_id", None),
            "sortings": self.sortings,
            "categories": Category.objects.all(),
        })
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_active=True).filter(quantity__gte=1)

        cat_id = self.kwargs.get("cat_id")
        if cat_id:
            qs = qs.filter(category__id=cat_id)

        query_order_by = self.request.GET.get("order_by")
        if query_order_by in list(self.sortings.keys()):
            qs = qs.order_by(query_order_by)
        else:
            qs = qs.order_by(self.default_order_by)

        return qs


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("products")

    def form_valid(self, form):
        user = form.save()

        if user:
            login(self.request, user)
            Cart.objects.create(user_id=user.id)

        return super().form_valid(form)


class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    next_page = reverse_lazy('home')
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('products')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))


class LogoutPageView(LogoutView):
    pass


class CartDetail(CustomerLoginRequiredMixin, TemplateView):
    template_name = "cart/cart-detail.html"

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart:
            return HttpResponseServerError()
        cart_items = cart.cartitem_set.select_related("product").all()

        context = self.get_context_data(**kwargs)
        context.update({
            "total_cost": cartitem_total_cost(cart_items),
            "cart_items": cart_items,
        })
        return self.render_to_response(context)


def cartitem_total_cost(cart_items):
    total_cost = 0
    for cart_item in cart_items:
        total_cost += cart_item.product.price * cart_item.count

    return total_cost


class CartProductAdd(CustomerLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart:
            return HttpResponseServerError()

        product_id = request.GET.get('product_id')
        add_count = request.GET.get('add_count', 1)
        if not product_id or not product_id.isdigit():
            return HttpResponseBadRequest('product_id not int')

        if not add_count.isdigit():
            return HttpResponseBadRequest('add_count not int')

        product_id = int(product_id)
        add_count = int(add_count)
        if add_count < 0:
            return HttpResponseBadRequest('add_count must be positive int')

        product = Product.objects.filter(id=product_id).filter(quantity__gte=1).first()
        if not product:
            return HttpResponseBadRequest('Товара нет в наличии')

        cart_item = CartItem.objects.filter(cart=cart).filter(product_id=product_id).first()
        if cart_item:  # only add if not exist
            new_count = cart_item.count + add_count
            if product.quantity < new_count:
                return HttpResponseBadRequest('Недостаточно товара')
            cart_item.count = new_count
            cart_item.save()
        else:
            CartItem.objects.create(cart=cart, product=product, count=add_count)

        return redirect("cart", permanent=False)


class CartProductDelete(CustomerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        product_id = request.GET.get('product_id')
        if not product_id or not product_id.isdigit():
            return HttpResponseBadRequest('product_id not int')

        product_id = int(product_id)

        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart:
            return HttpResponseServerError()

        cart_item = CartItem.objects.filter(cart=cart).filter(product__id=product_id).first()
        if not cart_item:
            return HttpResponseBadRequest('Нет такого товара в корзине')

        cart_item.delete()

        return redirect("cart")


class CartConfirm(CustomerLoginRequiredMixin, View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        return self.render_to_response({})


class OrdersList(View):
    # TODO: реализовать логику получения списка заказов пользователя
    pass


class OrderDetail(View):
    # TODO: реализовать логику получения детальной информации о заказе с выводов товаров в заказе
    pass


class OrderDelete(View):
    # TODO: реализовать логику удаления заказа. Проверять статус заказа
    pass
