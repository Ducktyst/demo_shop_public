from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, View, ListView, CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView

from shop.forms import RegisterForm, LoginForm, OrderResponseForm, SetCartItemCountForm
from shop.mixins import CustomerLoginRequiredMixin, SuperUserRequiredMixin
from shop.models import Product, Category, Cart, CartItem, Order, OrderItem


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
    template_name = "cart/cart_detail.html"

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
        # Проверить доступные товары.
        # Вывести сообщение каких товаров не хватает
        # заблокировать кнопку формирования заказа
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
            return HttpResponseServerError('cart not exists')

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


class CartProductUpdate(CustomerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('product_id')
        set_count = request.GET.get('set_count', 1)

        if not product_id or not product_id.isdigit():
            return HttpResponseBadRequest('product_id not int')

        if not set_count.isdigit():
            return HttpResponseBadRequest('set_count not int')

        product_id = int(product_id)
        set_count = int(set_count)

        return self.set_cart_count_id(request.user, product_id, set_count)

    def post(self, request, *args, **kwargs):
        form = SetCartItemCountForm(request.POST)
        if not form.is_valid():
            return redirect("cart", permanent=False)

        product_id = form.cleaned_data['product_id']
        set_count = form.cleaned_data['set_count']
        return self.set_cart_count_id(self.request.user, product_id, set_count)

    def set_cart_count_id(self, user, product_id: int, set_count: int):
        cart = Cart.objects.filter(user_id=user.id).first()
        if not cart:
            return HttpResponseServerError()

        if set_count < 0:
            return HttpResponseBadRequest('set_count must be positive')

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return HttpResponseBadRequest('Товар не существует')

        if product.quantity < set_count:
            return HttpResponseBadRequest('Недостаточно товара')

        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if cart_item:
            if cart_item.count != set_count:
                cart_item.count = set_count
                cart_item.save()
        else:
            CartItem.objects.create(cart=cart, product=product, count=set_count)

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
        user_id = request.user.id

        cart = Cart.objects.filter(user_id=user_id).first()
        if not cart:
            transaction.rollback()
            return HttpResponseServerError()

        order = Order.objects.create(
            user_id=user_id,
            status=Order.NEW,
            total_cost=0,
        )

        total_cost = 0
        for ci in cart.cartitem_set.select_related('product'):
            if ci.count > ci.product.quantity:
                transaction.rollback()
                return HttpResponseBadRequest("Недостаточно товара ")  # TODO: redirect to cart, with error message

            oi = OrderItem.objects.create(
                order_id=order.id,
                product=ci.product,
                count=ci.count,
            )
            total_cost += ci.count * ci.product.price
            ci.delete()

        order.total_cost = total_cost
        order.save()

        return redirect("orders")


class OrdersList(CustomerLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        context = {}
        context.update({"orders": Order.objects.filter(user=user).order_by('-created_at').all()})

        return render(request, "orders/orders.html", context)


class OrderDetail(CustomerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        order_id = kwargs.get('pk', None)

        order = Order.objects.filter(user=user).filter(id=order_id).first()  # todo: .prefetch_related("orderitem_set")?
        if order is None:
            return HttpResponseNotFound()

        context = {
            "order": order,
            "order_items": order.order_items.all()  # OrderItem -> fk(Order, related_name)
        }

        return render(request, "orders/order_detail.html", context)


class OrderDelete(CustomerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        order_id = kwargs.get('pk', None)
        if order_id is None:
            return HttpResponseNotFound()

        Order.objects.filter(user=user).filter(id=order_id).filter(status=Order.NEW).delete()
        return redirect('orders')


class AdminOrders(SuperUserRequiredMixin, ListView):
    template_name = "orders/admin_orders.html"
    model = Order
    context_object_name = "orders"
    paginate_by = '10'
    ordering = '-created_at'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context.update({
            'has_permission': True
        })
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status=Order.NEW)
        return qs


class AdminOrderResponse(SuperUserRequiredMixin, FormView):
    template_name = "orders/admin_order_response.html"
    form_class = OrderResponseForm

    def get(self, request, *args, **kwargs):
        return self.render_form(request, '', *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        order_id = kwargs.get('pk', None)

        if form.is_valid():
            if '_confirm' in request.POST:
                order_id = kwargs.get('pk', None)
                order = Order.objects.filter(pk=order_id).first()
                if order is None:
                    return HttpResponseNotFound()

                if order.status != Order.NEW:
                    return redirect('admin-orders')

                order.message = form.cleaned_data['message']
                order.status = Order.CONFIRMED
                order.save()

                return redirect('admin-order-response', pk=order_id)
            elif '_decline' in request.POST:
                order_id = kwargs.get('pk', None)
                order = Order.objects.filter(pk=order_id).first()
                if order is None:
                    return HttpResponseNotFound()

                if order.status != Order.NEW:
                    return redirect('admin-orders')

                order.message = form.cleaned_data['message']
                order.status = Order.DECLINED
                order.save()

                return redirect('admin-order-response', pk=order_id)

            return redirect('admin-order-response', pk=order_id)
        else:
            return self.render_form(request, 'Форма заполнена неверно', *args, **kwargs)

    def render_form(self, request, message, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        order_id = kwargs.get('pk', None)
        order = Order.objects.filter(pk=order_id).first()
        if order is None:
            return HttpResponseNotFound()

        if order.status != Order.NEW:  # Display Order. Block edit
            context.update({
                'order': order,
            })
            return render(self.request, self.template_name, context)

        context.update(
            {
                'order': order,
                'message': message,
            }
        )
        return self.render_to_response(context)
