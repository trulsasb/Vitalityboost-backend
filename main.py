from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from sqlalchemy.orm import Session

from models.models import Product
from routers import products, cart, payments, accounting, admin
from utils.env import settings

# Opprett FastAPI-app
app = FastAPI(
    title="VitalityBoost Backend",
    version="1.0"
)

# CORS – åpen for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Opprett databasetabeller
Base.metadata.create_all(bind=engine)

# --- SEED PRODUKT (kun hvis DB er tom) ---
def seed_products():
    with Session(engine) as db:
        if db.query(Product).first():
            return

        product = Product(
            name="VitalityBoost – Daglig støtte",
            description=(
                "Daglig kosttilskudd utviklet for voksne over 40 år "
                "som ønsker mer energi, bedre immunforsvar og sunn aldring."
            ),
            price=499
        )

        db.add(product)
        db.commit()

seed_products()
# ----------------------------------------

# Registrer API-ruter
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["Accounting"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Helse-sjekk
@app.get("/status")
def status():
    return {
        "status": "ok",
        "mode": settings.APP_MODE
    }


