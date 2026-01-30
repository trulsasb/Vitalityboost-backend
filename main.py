from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import products, cart, orders, user

# Opprett tabeller hvis de ikke finnes
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VitalityBoost API",
    version="1.0.0",
)

# CORS – enkel og trygg
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "VitalityBoost backend is running"}
