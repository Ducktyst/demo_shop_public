# https://docs.djangoproject.com/en/4.2/ref/contrib/admin/#overriding-the-default-admin-site
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.urls import reverse_lazy


class ShopAdminSite(admin.AdminSite):

    def get_app_list(self, request, app_label=None):
        apps = [
            {
                'name': 'Управление заказами',
                'models': [
                    {
                        'name': 'Заказы', 'perms': {'change': True},
                        'admin_url': reverse_lazy('admin-orders')
                    }
                ]
            }
        ]
        return apps + super().get_app_list(request, app_label)


class ShopAdminConfig(AdminConfig):
    default_site = 'demoproject.apps.ShopAdminSite'
