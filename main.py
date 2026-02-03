from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from payments.engine import PaymentEngine

# Routers
from routers import (
    products,
    cart,
    orders,
    user,
    admin_products,
    auth,
)
from payments import stripe_webhook, vipps_webhook

# Opprett tabeller hvis de ikke finnes
Base.metadata.create_all(bind=engine)

# Global PaymentEngine-instans (må eksistere før webhook-routers importeres)
payment_engine = PaymentEngine()

app = FastAPI(
    title="VitalityBoost API",
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# PUBLIC ROUTERS
# ---------------------------------------------------------
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(auth.router)

# ---------------------------------------------------------
# ADMIN ROUTERS
# ---------------------------------------------------------
app.include_router(user.router)            # nå admin-beskyttet
app.include_router(admin_products.router)

# ---------------------------------------------------------
# PAYMENT WEBHOOKS
# ---------------------------------------------------------
app.include_router(stripe_webhook.router, prefix="/webhooks/stripe")
app.include_router(vipps_webhook.router, prefix="/webhooks/vipps")

# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"message": "VitalityBoost backend is running"}
