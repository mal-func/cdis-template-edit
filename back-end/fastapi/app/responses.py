from fastapi import Response
from fastapi.responses import JSONResponse

def success(data, status_code: int = 200, response: Response | None = None):
    payload = {"success": True, "data": data}
    if response is not None:
        response.status_code = status_code
        return payload
    return JSONResponse(status_code=status_code, content=payload)

def error(status_code: int, code: str, message: str):
    return JSONResponse(status_code=status_code, content={"success": False, "error": {"code": code, "message": message}})
