from typing import TYPE_CHECKING, Iterable, Optional

from django.core.mail import EmailMultiAlternatives, get_connection

if TYPE_CHECKING:
    from django.core.mail.backends.smtp import EmailBackend


# subject, text_content, html_content, from_email, recipient_list
DataTuple = tuple[str, str, str, str, list[str]]


def send_mass_html_mail(
    datatuples: Iterable[DataTuple],
    fail_silently: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    connection: Optional['EmailBackend'] = None,
) -> int:
    """
    Send a mass HTML email, and return the number of emails sent.

    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=username, password=password, fail_silently=fail_silently
    )
    messages = []
    for subject, text, html, from_email, recipients in datatuples:
        message = EmailMultiAlternatives(
            subject,
            body=text,
            from_email=from_email,
            to=recipients,
        )
        message.attach_alternative(html, mimetype='text/html')
        messages.append(message)
    return connection.send_messages(messages)
