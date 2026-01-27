from fastapi import FastAPI
from database import Base, engine, get_db

# Routers
from routers import (
    products,
    cart,
    accounting,
    admin,
    vipps_initiate,
    vipps_webhook,
    stripe_initiate,
    stripe_webhook,
)
app = FastAPI()
@app.get("/")
def health():
    return {"status": "ok"}
    
# Payment engine + handlers
from payments.engine import PaymentEngine
from payments.vipps_handler import VippsHandler
from payments.stripe_handler import StripeHandler
from models.payment import PaymentProvider

# Create DB tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Vipps configuration
# -----------------------------
vipps_handler = VippsHandler(
    client_id="YOUR_VIPPS_CLIENT_ID",
    client_secret="YOUR_VIPPS_CLIENT_SECRET",
    subscription_key="YOUR_VIPPS_SUBSCRIPTION_KEY",
    merchant_serial_number="YOUR_MSN",
    base_url="https://apitest.vipps.no"
)

# -----------------------------
# Stripe configuration
# -----------------------------
stripe_handler = StripeHandler(
    api_key="YOUR_STRIPE_SECRET_KEY",
    webhook_secret="YOUR_STRIPE_WEBHOOK_SECRET"
)

# -----------------------------
# Payment Engine
# -----------------------------
payment_engine = PaymentEngine(
    handlers={
        PaymentProvider.VIPPS: vipps_handler,
        PaymentProvider.STRIPE: stripe_handler,
    },
    db_session_factory=get_db
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(accounting.router)
app.include_router(admin.router)

# Vipps
app.include_router(vipps_initiate.router)
app.include_router(vipps_webhook.router)

# Stripe
app.include_router(stripe_initiate.router)
app.include_router(stripe_webhook.router)

