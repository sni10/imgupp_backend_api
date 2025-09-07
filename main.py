from fastapi import FastAPI
from photomanager.api import router as photomanager_router

app = FastAPI()

# Подключение роутеров из приложения photomanager
app.include_router(photomanager_router, prefix="/api/img")
