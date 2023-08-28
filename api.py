from contextlib import asynccontextmanager
from os import environ

from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv(".env")
from fastapi import FastAPI
import uvicorn

import admin

PREFIX = "/smm_api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url = environ.get("DATABASE_URL").split("://", maxsplit=1)[-1]
    if db_url.startswith("/"):
        db_url = f"sqlite://{db_url}"
    else:
        db_url = f"postgresql+psycopg2://{db_url}"

    admin.app_init(app, db_url)

    yield


def app_init() -> FastAPI:
    return FastAPI(docs_url=f"{PREFIX}/docs", lifespan=lifespan)


app = app_init()


if __name__ == "__main__":
    uvicorn.run("api:app", host=environ.get("API_HOST"), reload=True, port=int(environ.get("API_PORT")))
