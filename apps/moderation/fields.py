import re
from pprint import pprint

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework.utils.encoders import JSONEncoder


def serialize(value_set):
    print(f'>>> before serialize: {value_set}')
    return serializers.serialize(
        'json',
        value_set,
        cls=JSONEncoder,
    )


def deserialize(value):
    print(f'>>> before deserialize:')
    pprint(re.match(r'.+("date".{30})', value).group(1))
    return serializers.deserialize(
        'json',
        value.encode(settings.DEFAULT_CHARSET),
        ignorenonexistent=True,
        cls=JSONEncoder,
    )


class SerializedObjectField(models.TextField):
    """
    Model field for storing a serialized model class instance.

    >>> from django.db import models
    >>> import SerializedObjectField
    >>> class A(models.Model):
            object = SerializedObjectField(serialize_format='json')
    >>> class B(models.Model):
            field = models.CharField(max_length=10)
    >>> b = B(field='test')
    >>> b.save()
    >>> a = A()
    >>> a.object = b
    >>> a.save()
    >>> a = A.object.get(pk=1)
    >>> a.object
    <B: B object>
    >>> a.object.__dict__
    {'field': 'test', 'id': 1}

    """

    def __init__(self, serialize_format: str = 'json', *args, **kwargs):
        self.serialize_format = serialize_format
        super().__init__(*args, **kwargs)

    def _serialize(self, value):
        print('\n>>> _serialize:')
        if not value:
            return ''
        value_set = [value]
        if value._meta.parents:
            value_set += [
                getattr(value, f.name)
                for f in list(value._meta.parents.values())
                if f is not None
            ]
        serialized_value = serialize(value_set)
        pprint(re.match(r'.+("date".{30})', serialized_value).group(1))
        return serialized_value

    def _deserialize(self, value):
        print('\n>>> _deserialize:')
        obj_generator = deserialize(value)
        obj = next(obj_generator).object
        for parent in obj_generator:
            for f in parent.object._meta.fields:
                try:
                    setattr(obj, f.name, getattr(parent.object, f.name))
                except ObjectDoesNotExist:
                    try:
                        # Try to set non-existant foreign key reference to None
                        setattr(obj, f.name, None)
                    except ValueError:
                        # Return None for changed_object if None not allowed
                        return None
        pprint(getattr(obj, 'date', ''))
        print('\n')
        return obj

    def db_type(self, connection=None):
        return 'text'

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        pre_save_value = self._serialize(value)
        print('\n>>> pre_save:')
        pprint(re.match(r'.+("date".{30})', pre_save_value).group(1))
        print('\n')
        return pre_save_value

    def contribute_to_class(self, cls, name):
        self.class_name = cls
        super().contribute_to_class(cls, name)
        models.signals.post_init.connect(self.post_init)

    def post_init(self, **kwargs):
        if 'sender' in kwargs and 'instance' in kwargs:
            sender = kwargs['sender']
            if (
                sender == self.class_name
                or sender._meta.proxy
                and issubclass(sender, self.class_name)
            ) and hasattr(kwargs['instance'], self.attname):
                print('\n>>> post_init >>>')
                instance = kwargs['instance']
                if isinstance(instance, str):
                    try:
                        pprint(
                            'changed_object: '
                            + re.match(
                                r'.+("date".{30})', kwargs['instance'].changed_object
                            ).group(1)
                        )
                    except Exception:
                        pass
                else:
                    try:
                        pprint('changed_object: ' + kwargs['instance'].changed_object.date)
                    except Exception:
                        pass
                value = self.value_from_object(kwargs['instance'])
                if value:
                    setattr(kwargs['instance'], self.attname, self._deserialize(value))
                else:
                    setattr(kwargs['instance'], self.attname, None)
                try:
                    pprint('value: ' + re.match(r'.+("date".{30})', value).group(1))
                except Exception as err:
                    print(value)
                print('exiting post_init\n')
