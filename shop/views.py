from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, View, ListView, CreateView
from django.contrib.auth.views import LoginView, LogoutView

from shop.forms import RegisterForm, LoginForm
from shop.models import Product, Category, Cart


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
