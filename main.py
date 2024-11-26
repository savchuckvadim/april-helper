import time

import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from src.api.endpoints import router as router_api_v1

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
    # "http://localhost:3000",  # Замените на ваш фронтенд-домен
    "https://april-server.ru",  # Другие разрешенные домены
]

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Укажите разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы
    allow_headers=["*"],  # Разрешенные заголовки
)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # await bot.send_message_admin_error(message=str(exc), domain=f'url: {request.url}\n\n query: {request.query_params}\n\nheaders: {request.headers}')
    return {"result": False}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
