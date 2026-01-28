import os
from fastapi import FastAPI

# Database session factory
from database import SessionLocal

# Payment engine + handlers
from payments.engine import PaymentEngine
from payments.vipps_handler import VippsHandler
from payments.stripe_handler import StripeHandler
from models.payment import PaymentProvider

# -----------------------------
#   FASTAPI APP
# -----------------------------

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

# -----------------------------
#   ROUTERS
# -----------------------------

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

# Products, cart, admin, accounting
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(accounting.router, prefix="/accounting", tags=["Accounting"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Vipps
app.include_router(vipps_initiate.router, prefix="/vipps", tags=["Vipps"])
app.include_router(vipps_webhook.router, prefix="/vipps-webhook", tags=["Vipps Webhook"])

# Stripe
app.include_router(stripe_initiate.router, prefix="/stripe", tags=["Stripe"])
app.include_router(stripe_webhook.router, prefix="/stripe-webhook", tags=["Stripe Webhook"])

# -----------------------------
#   ORDERS ROUTER (NY)
# -----------------------------

from routers.orders import router as orders_router
app.include_router(orders_router, prefix="/orders", tags=["Orders"])

# -----------------------------
#   PAYMENT HANDLERS
# -----------------------------

vipps_handler = VippsHandler(
    client_id=os.getenv("VIPPS_CLIENT_ID"),
    client_secret=os.getenv("VIPPS_CLIENT_SECRET"),
    subscription_key=os.getenv("VIPPS_SUBSCRIPTION_KEY"),
    merchant_serial_number=os.getenv("VIPPS_MSN"),
    base_url=os.getenv("VIPPS_BASE_URL"),
)

stripe_handler = StripeHandler(
    api_key=os.getenv("STRIPE_API_KEY"),
    webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
)

handlers = {
    PaymentProvider.VIPPS: vipps_handler,
    PaymentProvider.STRIPE: stripe_handler,
}

payment_engine = PaymentEngine(
    handlers=handlers,
    db_session_factory=SessionLocal
)
import reset_orders
