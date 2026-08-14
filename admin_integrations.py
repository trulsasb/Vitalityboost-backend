import requests
import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from payments.vipps_auth import VippsAuth
from routers.auth import get_current_owner
from utils.env import settings
from utils.integration_settings import get_setting, resolve_setting, set_settings

router = APIRouter(prefix="/admin/integrations", tags=["Admin Integrations"])

_owner_only = [Depends(get_current_owner)]

# Which credential fields each provider needs, and which ones are secret
# enough to mask in the UI rather than show in full (publishable keys are
# meant to be public, so they're shown as-is).
PROVIDER_FIELDS = {
    "stripe": {
        "secret_key": True,
        "publishable_key": False,
        "webhook_secret": True,
    },
    "vipps": {
        "client_id": False,
        "client_secret": True,
        "subscription_key": True,
        "msn": False,
        "base_url": False,
        "webhook_secret": True,
    },
}

_ENV_FALLBACKS = {
    ("stripe", "secret_key"): lambda: settings.STRIPE_SECRET_KEY,
    ("stripe", "webhook_secret"): lambda: settings.STRIPE_WEBHOOK_SECRET,
    ("vipps", "client_id"): lambda: settings.VIPPS_CLIENT_ID,
    ("vipps", "client_secret"): lambda: settings.VIPPS_CLIENT_SECRET,
    ("vipps", "subscription_key"): lambda: settings.VIPPS_SUBSCRIPTION_KEY,
    ("vipps", "msn"): lambda: settings.VIPPS_MSN,
    ("vipps", "base_url"): lambda: settings.VIPPS_BASE_URL,
    ("vipps", "webhook_secret"): lambda: settings.VIPPS_WEBHOOK_SECRET,
}


def _mask(value: str) -> str:
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:6]}…{value[-4:]}"


class IntegrationUpdate(BaseModel):
    values: dict[str, str]


@router.get("/{provider}", dependencies=_owner_only)
def get_integration_status(provider: str, db: Session = Depends(get_db)):
    if provider not in PROVIDER_FIELDS:
        raise HTTPException(status_code=404, detail="Unknown provider")

    result = {}
    for key, is_secret in PROVIDER_FIELDS[provider].items():
        db_value = get_setting(db, provider, key)
        env_fallback = _ENV_FALLBACKS.get((provider, key), lambda: None)()

        if db_value:
            source = "database"
            value = db_value
        elif env_fallback:
            source = "environment"
            value = env_fallback
        else:
            source = "unset"
            value = None

        result[key] = {
            "source": source,
            "preview": None if value is None else (_mask(value) if is_secret else value),
        }

    return result


@router.put("/{provider}", dependencies=_owner_only)
def update_integration(provider: str, payload: IntegrationUpdate, db: Session = Depends(get_db)):
    if provider not in PROVIDER_FIELDS:
        raise HTTPException(status_code=404, detail="Unknown provider")

    unknown = set(payload.values.keys()) - set(PROVIDER_FIELDS[provider].keys())
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown fields for {provider}: {sorted(unknown)}")

    set_settings(db, provider, payload.values)
    return {"status": "saved"}


@router.post("/{provider}/test", dependencies=_owner_only)
def test_integration(provider: str, db: Session = Depends(get_db)):
    if provider == "stripe":
        secret_key = resolve_setting(db, "stripe", "secret_key", settings.STRIPE_SECRET_KEY)
        if not secret_key:
            raise HTTPException(status_code=400, detail="No Stripe secret key configured yet")

        try:
            account = stripe.Account.retrieve(api_key=secret_key)
        except stripe.error.AuthenticationError:
            raise HTTPException(status_code=400, detail="Stripe rejected this secret key — check it's correct")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Could not reach Stripe: {e}")

        return {
            "status": "ok",
            "message": f"Connected to Stripe account {account.get('id')} ({account.get('email') or 'no email on file'})",
        }

    if provider == "vipps":
        client_id = resolve_setting(db, "vipps", "client_id", settings.VIPPS_CLIENT_ID)
        client_secret = resolve_setting(db, "vipps", "client_secret", settings.VIPPS_CLIENT_SECRET)
        subscription_key = resolve_setting(db, "vipps", "subscription_key", settings.VIPPS_SUBSCRIPTION_KEY)
        base_url = resolve_setting(db, "vipps", "base_url", settings.VIPPS_BASE_URL)

        if not all([client_id, client_secret, subscription_key]):
            raise HTTPException(
                status_code=400,
                detail="Fill in Client ID, Client Secret, and Subscription Key first",
            )

        auth = VippsAuth(
            client_id=client_id,
            client_secret=client_secret,
            subscription_key=subscription_key,
            base_url=base_url,
        )
        try:
            auth._fetch_new_token()
        except requests.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Vipps rejected these credentials: {e}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Could not reach Vipps: {e}")

        return {
            "status": "ok",
            "message": f"Connected to Vipps successfully ({base_url}). Note: this confirms Client ID/Secret/Subscription Key are valid, but not MSN — that's only checked when a real payment is initiated.",
        }

    raise HTTPException(status_code=501, detail=f"Connection test not implemented yet for {provider}")
