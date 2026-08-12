from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order
from models.product import Product
from services.fiken_service import FikenService
from services.tripletex_service import TripletexService
from utils.env import settings

router = APIRouter(prefix="/admin/accounting", tags=["Admin Accounting"])


def _build_line_items(order: Order, db: Session):
    lines = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        lines.append({
            "description": product.name if product else f"Product #{item.product_id}",
            "quantity": item.quantity,
            "unitPrice": item.price_at_purchase,
        })
    return lines


@router.get("/status")
def accounting_status():
    """Which accounting provider(s) are configured and ready to use."""
    return {
        "tripletex_configured": bool(settings.TRIPLETEX_TOKEN),
        "fiken_configured": bool(settings.FIKEN_API_KEY),
    }


@router.post("/orders/{order_id}/send-to-tripletex")
async def send_order_to_tripletex(order_id: int, db: Session = Depends(get_db)):
    if not settings.TRIPLETEX_TOKEN:
        raise HTTPException(status_code=503, detail="Tripletex is not configured (missing TRIPLETEX_TOKEN)")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    service = TripletexService()
    invoice_data = {
        "orderReference": str(order.id),
        "currency": "NOK",
        "orderLines": _build_line_items(order, db),
    }
    result = await service.post_invoice(invoice_data)
    return {"order_id": order.id, "tripletex_response": result}


@router.post("/orders/{order_id}/send-to-fiken")
async def send_order_to_fiken(order_id: int, db: Session = Depends(get_db)):
    if not settings.FIKEN_API_KEY:
        raise HTTPException(status_code=503, detail="Fiken is not configured (missing FIKEN_API_KEY)")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    service = FikenService()
    invoice_data = {
        "orderReference": str(order.id),
        "currency": "NOK",
        "lines": _build_line_items(order, db),
    }
    result = await service.push_invoice(invoice_data)
    return {"order_id": order.id, "fiken_response": result}
