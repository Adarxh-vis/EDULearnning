from bson import ObjectId
from typing import Any, Dict, List

def to_str_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB ObjectId fields to string for JSON serialization.
    """
    if not doc:
        return doc
    out = dict(doc)
    if "_id" in out and isinstance(out["_id"], ObjectId):
        out["_id"] = str(out["_id"])
    return out

def serialize_list(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [to_str_id(d) for d in docs]

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize a single document by converting ObjectId to string.
    """
    return to_str_id(doc)
