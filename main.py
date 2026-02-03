from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Standard routers
from products import router as products_router

# Payments module
from payments import router as payments_router

# Admin modules
from admin_orders import router as admin_orders_router
from admin_payments import router as admin_payments_router
from admin_products import router as admin_products_router
from admin_users import router as admin_users_router


app = FastAPI(title="VitalityBoost Backend")

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Juster senere for produksjon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# PUBLIC ROUTERS
# ---------------------------------------------------------

app.include_router(products_router)

# ---------------------------------------------------------
# PAYMENTS ROUTER
# ---------------------------------------------------------

app.include_router(payments_router)

# ---------------------------------------------------------
# ADMIN ROUTERS
# ---------------------------------------------------------

app.include_router(admin_orders_router)
app.include_router(admin_payments_router)
app.include_router(admin_products_router)
app.include_router(admin_users_router)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"message": "VitalityBoost backend is running"}
