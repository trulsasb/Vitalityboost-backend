from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_admin
from utils.env import settings
from utils.site_settings import get_site_setting, set_site_setting

router = APIRouter(prefix="/admin/contact-settings", tags=["Admin Contact Settings"])

_admin_only = [Depends(get_current_admin)]

CONTACT_EMAIL_KEY = "contact_notify_email"


class ContactSettingsUpdate(BaseModel):
    notify_email: EmailStr


@router.get("", dependencies=_admin_only)
def get_contact_settings(db: Session = Depends(get_db)):
    value = get_site_setting(db, CONTACT_EMAIL_KEY) or settings.CONTACT_EMAIL
    return {"notify_email": value}


@router.put("", dependencies=_admin_only)
def update_contact_settings(payload: ContactSettingsUpdate, db: Session = Depends(get_db)):
    set_site_setting(db, CONTACT_EMAIL_KEY, payload.notify_email)
    return {"notify_email": payload.notify_email}
