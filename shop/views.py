from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, View, ListView

from shop.models import Product, Category


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
