from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class PasswordChangeView(auth_views.PasswordChangeView):
    """
    Allow a user to change their password.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordChangeView
    """

    template_name = 'account/password_change_form.html'
    success_url = reverse_lazy('account:password_change_done')


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """
    The page shown after a user has changed their password.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordChangeDoneView
    """

    template_name = 'account/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    """
    Allow a user to reset their password by generating a one-time-use link.

    Sends the link to the user’s registered email address.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView
    """

    template_name = 'account/password_reset_form.html'
    email_template_name = 'account/password_reset_email.html'
    success_url = reverse_lazy('account:password_reset_done')


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    """
    The page shown after a user has been emailed a link to reset their password.

    This view is called by default if PasswordResetView does not explicitly set success_url.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetDoneView
    """

    template_name = 'account/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Present a form for entering a new password.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView
    """

    template_name = 'account/password_reset_confirm.html'


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """
    Present a view which informs the user that the password has been successfully changed.

    https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView
    """

    template_name = 'account/password_reset_complete.html'
