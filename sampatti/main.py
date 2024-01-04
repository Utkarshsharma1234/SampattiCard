from fastapi import FastAPI, Response, Request
from . import models,schemas
from .database import engine
from .routers import user

app = FastAPI()

models.Base.metadata.create_all(engine)


app.include_router(user.router)