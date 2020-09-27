from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class PasswordChangeView(auth_views.PasswordChangeView):
    """TODO: add docstring."""

    template_name = 'account/password_change_form.html'
    success_url = reverse_lazy('account:password_change_done')


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """TODO: add docstring."""

    template_name = 'account/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    """TODO: add docstring."""

    template_name = 'account/password_reset_form.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account:password_reset_done')


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """TODO: add docstring."""

    template_name = 'account/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """TODO: add docstring."""

    template_name = 'account/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """TODO: add docstring."""
    template_name = 'account/password_reset_complete.html'
