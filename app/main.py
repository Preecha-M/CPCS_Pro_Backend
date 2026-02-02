import os
import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers.health import router as health_router
from .routers.pages import router as pages_router
from .routers.line_callback import router as line_router
from .routers.admin_dashboard import router as admin_router
from .routers.admin_api import router as admin_api_router
from .routers.auth_api import router as auth_api_router
from .routers.admin_history_detail import router as admin_history_router
from .routers.dev_dashboard import router as dev_dashboard_router
from . import line_handlers 
from app.routers import auth_api
from .routers import wind_api



app = FastAPI()

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(wind_api.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
