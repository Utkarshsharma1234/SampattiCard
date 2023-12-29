from fastapi import FastAPI
from . import models
from .database import engine
from .routers import user

app = FastAPI()

models.Base.metadata.create_all(engine)

@app.get("/")
def home():
    return {
        "data" : "Hello"
    }

app.include_router(user.router)