import os

import toml
import yaml
from github import Github
from invoke.context import Context
from toml.encoder import TomlEncoder, _dump_str

from apps.propositions.models import (
    Proposition,
)
from core.models.slugged_model import SluggedModel
from core.utils import github

CMS_MODELS = ('propositions', Proposition)

context = Context()
for directory_name, model_cls in CMS_MODELS:
    context.run(f'mkdir -p _content/{directory_name}')
    with context.cd(f'/modularhistory/_content/{directory_name}'):
        instance: SluggedModel
        for instance in model_cls.objects.all():
            context.run(f'mkdir -p {instance.slug}')
            serialized_instance = instance.serialize()
            for key in model_cls.modifiable_fields:
                value = serialized_instance[key]
                filename = os.path.join(instance.slug, key)
                with open(
                    f'/modularhistory/_content/{directory_name}/{filename}', 'w'
                ) as file:
                    file.write(str(value))
                print(filename)
