from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("login-customer")

    def test_func(self):
        return self.request.user.is_superuser


class CustomerLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("login-customer")


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("login-customer")

    def test_func(self):
        return self.request.user.is_superuser
