from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.errors import AppError, app_error_handler
from app.jobs import job_queue
from app.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await job_queue.start()
    try:
        yield
    finally:
        await job_queue.stop()


app = FastAPI(title="EMATA Runtime Rebuild", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(AppError, app_error_handler)
app.include_router(router)
