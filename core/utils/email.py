from typing import TYPE_CHECKING

from django.core.mail import EmailMultiAlternatives, get_connection

if TYPE_CHECKING:
    from django.core.mail.backends.smtp import EmailBackend


def send_mass_html_mail(
    datatuples,
    fail_silently=False,
    user=None,
    password=None,
    connection=None,
):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection: 'EmailBackend' = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently
    )
    messages = []
    for subject, text, html, from_email, recipient in datatuples:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)
