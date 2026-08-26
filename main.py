from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from admin_accounting import router as admin_accounting_router
from admin_categories import router as admin_categories_router
from admin_contact import router as admin_contact_router
from admin_content import router as admin_content_router
from admin_discounts import router as admin_discounts_router
from admin_integrations import router as admin_integrations_router
from admin_orders import router as admin_orders_router
from admin_payments import router as admin_payments_router
from admin_products import router as admin_products_router
from admin_users import router as admin_users_router
from payments.router import router as payments_router
from routers.auth import router as auth_router, get_current_admin, require_permission
from routers.cart import router as cart_router
from routers.contact import router as public_contact_router
from routers.content import router as public_content_router
from routers.discounts import router as public_discounts_router
from routers.orders import router as public_orders_router
from routers.products import router as public_products_router
from routers.stripe_webhook import router as stripe_webhook_router
from routers.vipps_webhook import router as vipps_webhook_router
from utils.env import settings

app = FastAPI(title="VitalityBoost Backend")

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    # The production frontend plus localhost dev origins — without the
    # latter, running the Next.js dev server locally against this live
    # backend silently fails every direct client-side GET (e.g. homepage
    # content), which then falls back to defaults, masking saved changes.
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

_admin_guard = [Depends(get_current_admin)]
_accounting_guard = [Depends(require_permission("can_manage_accounting"))]

app.include_router(auth_router)
# Orders, payments, and products enforce permissions per-route (view vs.
# edit) inside their own router files, so no blanket dependency here.
app.include_router(admin_categories_router)
app.include_router(admin_orders_router)
app.include_router(admin_payments_router)
app.include_router(admin_products_router)
app.include_router(admin_users_router, dependencies=_admin_guard)
app.include_router(admin_accounting_router, dependencies=_accounting_guard)
app.include_router(admin_contact_router)
app.include_router(admin_content_router)
app.include_router(admin_discounts_router)
app.include_router(admin_integrations_router)
app.include_router(payments_router)
app.include_router(cart_router)
app.include_router(public_contact_router)
app.include_router(public_content_router)
app.include_router(public_discounts_router)
app.include_router(public_orders_router)
app.include_router(public_products_router)
# Webhooks: no admin auth (verified via provider signature instead), and
# not user-facing, so they aren't gated behind login either.
app.include_router(stripe_webhook_router)
app.include_router(vipps_webhook_router)

# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()

# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "VitalityBoost Backend"}
