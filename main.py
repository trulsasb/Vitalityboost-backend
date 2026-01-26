from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import products, cart, payments, accounting, admin

# Opprett tabeller hvis de ikke finnes
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS – disse MÅ ligge etter app = FastAPI()
app.include_router(products.router, prefix="/products")
app.include_router(cart.router, prefix="/cart")
app.include_router(payments.router, prefix="/payments")
app.include_router(accounting.router, prefix="/accounting")
app.include_router(admin.router, prefix="/admin")

@app.get("/")
def root():
    return {"message": "VitalityBoost backend is running"}
