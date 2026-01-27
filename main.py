from fastapi import FastAPI

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

# Health check
@app.get("/")
def health():
    return {"status": "ok"}


# -----------------------------
#   ROUTER MOUNTING
# -----------------------------

# Products
app.include_router(products.router, prefix="/products", tags=["Products"])

# Cart
app.include_router(cart.router, prefix="/cart", tags=["Cart"])

# Accounting
app.include_router(accounting.router, prefix="/accounting", tags=["Accounting"])

# Admin
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Vipps
app.include_router(vipps_initiate.router, prefix="/vipps", tags=["Vipps"])
app.include_router(vipps_webhook.router, prefix="/vipps-webhook", tags=["Vipps Webhook"])

# Stripe
app.include_router(stripe_initiate.router, prefix="/stripe", tags=["Stripe"])
app.include_router(stripe_webhook.router, prefix="/stripe-webhook", tags=["Stripe Webhook"])
