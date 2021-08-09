from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.manager import Manager
from django.template.loader import render_to_string

from apps.moderation.models.moderated_model.manager import ModeratedModelManager

from .message_backends import (
    BaseMessageBackend,
    BaseMultipleMessageBackend,
    EmailMessageBackend,
    EmailMultipleMessageBackend,
)


class GenericModerator:
    """
    Encapsulates moderation options for a given model.
    """

    resolve_foreignkeys = True
    message_backend_class = EmailMessageBackend
    multiple_message_backend_class = EmailMultipleMessageBackend
    subject_template_moderator = 'moderation/notification_subject_moderator.txt'
    message_template_moderator = 'moderation/notification_message_moderator.txt'
    subject_template_user = 'moderation/notification_subject_user.txt'
    message_template_user = 'moderation/notification_message_user.txt'

    def reason(self, reason, user=None, obj=None):
        """Returns moderation reason for auto moderation.  Optional user
        and object can be passed for a more custom reason.
        """
        return reason

    def _check_user_in_groups(self, user, groups):
        for group in groups:
            try:
                group = Group.objects.get(name=group)
            except ObjectDoesNotExist:
                return False

            if group in user.groups.all():
                return True

        return False

    def get_message_backend(self):
        if not issubclass(self.message_backend_class, BaseMessageBackend):
            raise TypeError(
                "The message backend used '%s' needs to "
                'inherit from the BaseMessageBackend '
                'class' % self.message_backend_class
            )
        return self.message_backend_class()

    def get_multiple_message_backend(self):
        if not issubclass(self.multiple_message_backend_class, BaseMultipleMessageBackend):
            raise TypeError(
                "The message backend used '{}' needs to "
                'inherit from the BaseMultipleMessageBackend '
                'class'.format(self.message_backend_class)
            )
        return self.multiple_message_backend_class()

    def send(
        self,
        content_object,
        subject_template,
        message_template,
        recipient_list,
        extra_context=None,
    ):
        context = {
            'moderation': content_object.moderation,
            'content_object': content_object,
            'site': Site.objects.get_current(),
            'content_type': content_object.moderation.content_type,
        }

        if extra_context:
            context.update(extra_context)

        message = render_to_string(message_template, context)
        subject = render_to_string(subject_template, context)

        backend = self.get_message_backend()
        backend.send(subject=subject, message=message, recipient_list=recipient_list)

    def send_many(self, queryset, subject_template, message_template, extra_context=None):
        site = Site.objects.get_current()

        ctx = extra_context if extra_context else {}

        datatuples = tuple(
            {
                'subject': render_to_string(
                    subject_template,
                    ctx.update(
                        {
                            'moderation': mobj,
                            'content_object': mobj.content_object,
                            'site': site,
                            'content_type': mobj.content_type,
                            'user': mobj.changed_by,
                        }
                    ),
                ),
                'message': render_to_string(
                    message_template,
                    ctx.update(
                        {
                            'moderation': mobj,
                            'content_object': mobj.content_object,
                            'site': site,
                            'content_type': mobj.content_type,
                            'user': mobj.changed_by,
                        }
                    ),
                ),
                # from_email will need to be added
                'recipient_list': [mobj.changed_by.email],
            }
            for mobj in queryset
        )

        multiple_backend = self.get_multiple_message_backend()
        multiple_backend.send(datatuples)

    def inform_moderator(self, content_object, extra_context=None):
        """Send notification to moderator"""

        if self.notify_moderator:
            self.send(
                content_object=content_object,
                subject_template=self.subject_template_moderator,
                message_template=self.message_template_moderator,
                recipient_list=settings.MODERATORS,
                extra_context=extra_context,
            )

    def inform_user(self, content_object, user, extra_context=None):
        """
        Send notification to user when object is approved or rejected
        """
        if extra_context:
            extra_context.update({'user': user})
        else:
            extra_context = {'user': user}
        if self.notify_user:
            self.send(
                content_object=content_object,
                subject_template=self.subject_template_user,
                message_template=self.message_template_user,
                recipient_list=[user.email],
                extra_context=extra_context,
            )

    def inform_users(self, queryset, extra_context=None):
        """
        Send notifications to users when their objects are approved or rejected
        """
        if self.notify_user:
            self.send_many(
                queryset=queryset.exclude(changed_by=None).select_related(
                    'changed_by__email'
                ),
                subject_template=self.subject_template_user,
                message_template=self.message_template_user,
                extra_context=extra_context,
            )
