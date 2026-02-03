from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_orders import router as admin_orders_router
from admin_payments import router as admin_payments_router
from admin_products import router as admin_products_router
from admin_users import router as admin_users_router
from payments.router import router as payments_router

app = FastAPI(title="VitalityBoost Backend")

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
# ROUTERS
# ---------------------------------------------------------

app.include_router(admin_orders_router)
app.include_router(admin_payments_router)
app.include_router(admin_products_router)
app.include_router(admin_users_router)
app.include_router(payments_router)

# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "VitalityBoost Backend"}
