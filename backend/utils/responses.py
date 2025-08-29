from typing import Any, Optional

def success_response(data: Any = None, message: str = "Success") -> dict:
    response = {"status": "ok", "message": message}
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
    return response

def error_response(message: str, status: str = "error") -> dict:
    return {"status": status, "message": message}