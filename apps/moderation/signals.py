import django.dispatch

pre_moderation = django.dispatch.Signal(providing_args=['instance', 'status'])

post_moderation = django.dispatch.Signal(providing_args={'instance', 'status'})

pre_many_moderation = django.dispatch.Signal(
    providing_args={'queryset', 'status', 'moderator', 'reason'}
)

post_many_moderation = django.dispatch.Signal(
    providing_args={'queryset', 'status', 'moderator', 'reason'}
)
