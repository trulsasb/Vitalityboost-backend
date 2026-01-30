from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import products, orders, payments
from payments.vipps_handler import VippsHandler
from payments.stripe_handler import StripeHandler

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Handlers (ingen argumenter lenger)
vipps_handler = VippsHandler()
stripe_handler = StripeHandler()

# Routers
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])


@app.get("/")
def root():
    return {"message": "VitalityBoost backend running"}
