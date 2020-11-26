import json
import logging
from pprint import pformat
from typing import Any, Dict, Iterable, Mapping

from prettyjson import PrettyJSONWidget

from modularhistory.utils.html import soupify


class JSONEditorWidget(PrettyJSONWidget):
    """Widget for editing JSON values."""

    # def __init__(self, attrs=None, mode='form', options=None, width=None, height=None):
    #     """Construct the JSON editor widget."""
    #     # Prevent use of django_json_widget's default height
    #     attrs = attrs or {'style': 'display: inline-block; width: 90%;'}

    #     super().__init__(
    #         attrs=attrs, mode=mode, options=options, width=width, height=height
    #     )

    def value_from_datadict(
        self, data: Dict[str, Any], files: Mapping[str, Iterable[Any]], name: str
    ) -> str:
        """
        Process the value returned from the JSON editor.

        Return the value to be saved.
        """
        json_value = super().value_from_datadict(data, files, name)
        if isinstance(json_value, dict):
            json_data = json_value
        else:
            logging.debug(f'JSON string from editor: {json_value}')
            try:
                json_data = json.loads(soupify(json_value).get_text())
            except Exception as err:
                logging.error(
                    f'Loading value from JSON editor widget resulted in {err}'
                )
                return json_value
        logging.debug(f'JSON before removing null attributes: {pformat(json_data)}')
        json_data = {
            attribute: attribute_value
            for attribute, attribute_value in json_data.items()
            if attribute_value is not None
        }
        logging.debug(f'JSON after removing null attributes: {pformat(json_data)}')
        return json.dumps(json_data)
