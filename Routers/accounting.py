from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..services.tripletex_service import TripletexService
from ..services.fiken_service import FikenService
from .. import models, database

router = APIRouter()

class ExportIn(BaseModel):
    provider: str  # tripletex | fiken
    invoice_data: dict

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/export")
async def export_invoice(payload: ExportIn, db: Session = Depends(get_db)):
    provider_cfg = db.query(models.AccountingIntegration).filter(
        models.AccountingIntegration.provider == payload.provider
    ).first()
    if not provider_cfg or not provider_cfg.api_key:
        raise HTTPException(status_code=400, detail="Integration not configured")

    if payload.provider == "tripletex":
        result = await TripletexService(api_key=provider_cfg.api_key,
                                        test_mode=provider_cfg.test_mode).post_invoice(payload.invoice_data)
    elif payload.provider == "fiken":
        result = await FikenService(api_key=provider_cfg.api_key,
                                    test_mode=provider_cfg.test_mode).push_invoice(payload.invoice_data)
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")

    return {"status": "exported", "result": result}
