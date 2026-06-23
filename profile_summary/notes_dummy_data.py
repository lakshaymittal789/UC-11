from typing import Any
import json
import os

NoteRecord = dict[str, Any]

# Load dummy data from the root dummy_data.json file
_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dummy_data.json')
with open(_json_path, 'r', encoding='utf-8') as _f:
    NOTES: list[NoteRecord] = json.load(_f)
