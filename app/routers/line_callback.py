from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from ..line_handlers.callback import handle_events

router = APIRouter()

@router.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers.get("x-line-signature", "")
    background_tasks.add_task(handle_events, body, signature)
    return JSONResponse(content={"message": "OK"}, status_code=200)
