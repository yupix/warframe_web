import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates


load_dotenv()

db_user = os.environ.get('WEB_DB_USER')
db_port = os.environ.get('WEB_DB_PORT')
db_host = os.environ.get('WEB_DB_HOST')
db_password = os.environ.get('WEB_DB_PASSWORD')
db_default_database = os.environ.get('WEB_DB_NAME')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
templates = Jinja2Templates(directory="./app/templates")

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_default_database}', echo=False)  # DEBUG時はTrueに

Session = sessionmaker(bind=engine, autoflush=True)
session = Session()

Base = declarative_base()

from app.router import warframe_main
from app.router.api import news

app.include_router(warframe_main.router)
app.include_router(news.router)
