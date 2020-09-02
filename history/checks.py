# TODO
import re
from typing import List
from django.core.checks import register
from django.core.checks.messages import CheckMessage, DEBUG, INFO, WARNING, ERROR
from django.conf import settings

from mypy import api


# # The check framework is used for multiple different kinds of checks. As such, errors
# # and warnings can originate from models or other django objects. The `CheckMessage`
# # requires an object as the source of the message and so we create a temporary object
# # that simply displays the file and line number from mypy (i.e. "location")
# class MyPyErrorLocation:
#     def __init__(self, location):
#         self.location = location
#
#     def __str__(self) -> str:
#         """TODO: write docstring."""
#         return self.location
#
#
# @register()
# def mypy(app_configs, **kwargs) -> List:
#     print('Performing mypy checks...\n')
#
#     # By default run mypy against the whole database everytime checks are performed.
#     # If performance is an issue then `app_configs` can be inspected and the scope
#     # of the mypy check can be restricted
#     mypy_args = [settings.BASE_DIR]
#     results = api.run(mypy_args)
#     error_messages = results[0]
#
#     if not error_messages:
#         return []
#
#     # Example: myproject/checks.py:17: error: Need type annotation for 'errors'
#     pattern = re.compile(r'^(.+\d+): (\w+): (.+)')
#
#     errors = []
#     for message in error_messages.rstrip().split('\n'):
#         parsed = re.match(pattern, message)
#         if not parsed:
#             continue
#
#         location = parsed.group(1)
#         mypy_level = parsed.group(2)
#         message = parsed.group(3)
#
#         # level = DEBUG
#         # if mypy_level == 'note':
#         #     level = INFO
#         # elif mypy_level == 'warning':
#         #     level = WARNING
#         # elif mypy_level == 'error':
#         #     level = ERROR
#         # else:
#         #     print(f'Unrecognized mypy level: {mypy_level}')
#
#         errors.append(CheckMessage(WARNING, message, obj=MyPyErrorLocation(location)))
#
#     return errors
