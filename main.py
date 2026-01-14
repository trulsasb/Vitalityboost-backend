from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import products, cart, payments, accounting, admin
from .database import Base, engine
from .utils.env import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VitalityBoost Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Include routes
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["Accounting"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/status")
async def status():
    return {"status": "ok", "mode": settings.APP_MODE}
