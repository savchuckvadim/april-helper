import time

import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import router as router_api_v1
from src.api.http.exceptions import AppException

from tgbot import TelegramBot


from dotenv import load_dotenv

load_dotenv()

bot = TelegramBot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.version = "0.1.0"


app.include_router(router=router_api_v1, prefix="/api/v1")

origins = [
    "http://localhost:5000",  # Замените на ваш фронтенд-домен
    "https://april-server.ru",  # Другие разрешенные домены
    "https://front.april-app.ru",
]

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Укажите разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы
    allow_headers=["*"],  # Разрешенные заголовки
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
