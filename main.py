from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import products, cart, orders, user
from payments.engine import PaymentEngine

# Opprett tabeller hvis de ikke finnes
Base.metadata.create_all(bind=engine)

# Global PaymentEngine-instans (må være før webhook-routers importeres)
payment_engine = PaymentEngine()

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

# Webhook-routers (må inkluderes etter payment_engine er definert)
from payments import stripe_webhook, vipps_webhook
app.include_router(stripe_webhook.router, prefix="/webhooks/stripe")
app.include_router(vipps_webhook.router, prefix="/webhooks/vipps")

@app.get("/")
def root():
    return {"message": "VitalityBoost backend is running"}
