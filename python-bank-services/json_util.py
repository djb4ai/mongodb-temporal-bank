import json
import datetime
from typing import Any, Dict

def serialize_to_json(obj: Any) -> str:
    """
    Serialize an object to JSON string.
    
    Args:
        obj: The object to serialize
        
    Returns:
        A JSON string
    """
    return json.dumps(obj, cls=JSONEncoder)

def parse_json(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string into a dictionary.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        A dictionary representation of the JSON
    """
    return json.loads(json_str)

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB objects and dates."""
    
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if hasattr(obj, '_id'):
            # Handle MongoDB ObjectID
            obj_dict = obj.copy()
            if '_id' in obj_dict:
                obj_dict['_id'] = str(obj_dict['_id'])
            return obj_dict
        return json.JSONEncoder.default(self, obj)