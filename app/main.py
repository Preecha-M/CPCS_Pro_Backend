import os
import traceback
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .middleware.access_audit import AccessAuditMiddleware
from .routers.health import router as health_router
from .routers.pages import router as pages_router
from .routers.line_callback import router as line_router
from .routers.admin_dashboard import router as admin_router
from .routers.admin_api import router as admin_api_router
from .routers.auth_api import router as auth_api_router
from .routers.admin_history_detail import router as admin_history_router
from .routers.dev_dashboard import router as dev_dashboard_router
from .routers.activity_api import router as activity_api_router
from .routers.admin_logs import router as admin_logs_router
from . import line_handlers
from .routers import wind_api
from .services.audit_log import insert_audit


app = FastAPI()

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AccessAuditMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    if isinstance(exc, RequestValidationError):
        return await request_validation_exception_handler(request, exc)
    tb = traceback.format_exc()
    try:
        insert_audit(
            "system_error",
            {
                "path": request.url.path[:1024],
                "method": request.method,
                "error_type": type(exc).__name__,
                "message": str(exc)[:2000],
                "traceback": tb[-8000:],
            },
        )
    except Exception:
        pass
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
if os.path.isdir("guide_images"):
    app.mount("/guide_images", StaticFiles(directory="guide_images"), name="guide_images")

app.include_router(health_router)
app.include_router(pages_router)
app.include_router(line_router)
app.include_router(admin_router)
app.include_router(admin_api_router, prefix="/api")
app.include_router(auth_api_router, prefix="/api")
app.include_router(admin_history_router, prefix="/api")
app.include_router(dev_dashboard_router, prefix="/api")
app.include_router(activity_api_router, prefix="/api")
app.include_router(admin_logs_router, prefix="/api")
app.include_router(wind_api.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
