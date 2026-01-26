from fastapi import FastAPI
from database import Base, engine
from routers import products, cart, payments, accounting, admin

Base.metadata.create_all(bind=engine)

app = FastAPI()
