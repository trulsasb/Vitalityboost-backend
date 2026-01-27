from fastapi import FastAPI
from database import Base, engine
from routers import products, cart, payments, accounting, admin

from payments.engine import PaymentEngine
from payments.vipps_handler import VippsHandler
from models.payment import PaymentProvider

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(payments.router)
app.include_router(accounting.router)
app.include_router(admin.router)

# Vipps
app.include_router(vipps_initiate.router)
app.include_router(vipps_webhook.router)

# Vipps config (sett inn dine egne nøkler senere)
vipps_handler = VippsHandler(
    client_id="YOUR_VIPPS_CLIENT_ID",
    client_secret="YOUR_VIPPS_CLIENT_SECRET",
    subscription_key="YOUR_VIPPS_SUBSCRIPTION_KEY",
    merchant_serial_number="YOUR_MSN",
    base_url="https://apitest.vipps.no"  # byttes til prod senere
)

payment_engine = PaymentEngine(
    handlers={
        PaymentProvider.VIPPS: vipps_handler
    },
    db_session_factory=get_db
)
