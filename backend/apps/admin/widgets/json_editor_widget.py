import json
import logging
from pprint import pformat
from typing import Any, Iterable, Mapping

from flat_json_widget.widgets import FlatJsonWidget

from core.utils.html import soupify


class JSONEditorWidget(FlatJsonWidget):
    """Widget for editing JSON values."""

    def value_from_datadict(
        self, data: dict[str, Any], files: Mapping[str, Iterable[Any]], name: str
    ) -> str:
        """
        Process the value returned from the JSON editor.

        Return the value to be saved.
        """
        json_value = super().value_from_datadict(data, files, name)
        if isinstance(json_value, (dict, list)):
            json_data = json_value
        else:
            logging.debug(f'JSON string from editor: {json_value}')
            try:
                json_data = json.loads(soupify(json_value).get_text())
            except Exception as err:
                logging.error(f'Error loading value from JSON editor widget: {err}')
                return json_value
        if isinstance(json_data, dict):
            logging.debug(f'JSON before removing null attributes: {pformat(json_data)}')
            json_data = {
                attribute: attribute_value
                for attribute, attribute_value in json_data.items()
                if attribute_value is not None
            }
            logging.debug(f'JSON after removing null attributes: {pformat(json_data)}')
        return json.dumps(json_data)
