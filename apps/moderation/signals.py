import django.dispatch

post_moderation = django.dispatch.Signal(providing_args={'instance', 'status'})

post_many_moderation = django.dispatch.Signal(
    providing_args={'queryset', 'status', 'moderator', 'reason'}
)
