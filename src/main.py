import time

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.auth import router as auth_router
from src.api.category import router as category_router
from src.api.task import router as task_router
from src.core.exceptions import (
    AppError,
    AuthenticationError,
    TaskNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.core.ioc import AppProvider
from src.core.lifespan import lifespan
from src.core.limiter import limiter
from src.core.logger import logger
from src.services.auth import oauth2_scheme

container = make_async_container(AppProvider())

app = FastAPI(title="Task Tracker API", lifespan=lifespan)

setup_dishka(container, app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host if request.client else "Unknown"
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url} from {client_ip}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Outgoing response: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s"
    )

    return response


@app.exception_handler(AppError)
async def global_exception_handler(request: Request, exc: AppError):
    status_map = {
        UserAlreadyExistsError: 400,
        AuthenticationError: 401,
        UserNotFoundError: 404,
        TaskNotFoundError: 404,
        AppError: 400,
    }

    status_code = status_map.get(type(exc), 400)

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


app.include_router(auth_router, prefix="/api")
app.include_router(task_router, prefix="/api", dependencies=[Depends(oauth2_scheme)])
app.include_router(
    category_router, prefix="/api", dependencies=[Depends(oauth2_scheme)]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
