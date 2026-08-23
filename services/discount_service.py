from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, or_, update
from sqlalchemy.orm import Session

from models.discount import DiscountCode


@dataclass
class DiscountCheckItem:
    product_id: int
    quantity: int
    price: float


@dataclass
class DiscountResult:
    valid: bool
    message: str
    discount_amount: float = 0.0
    discount_code: DiscountCode | None = None


def check_discount_code(
    db: Session,
    code: str,
    items: list[DiscountCheckItem],
    customer_email: str | None,
) -> DiscountResult:
    """Single source of truth for discount validation and amount calculation —
    used by both the live /discounts/validate preview and real order creation,
    so a code can never be accepted at checkout preview but rejected (or
    computed differently) when the order is actually placed."""

    if not code or not code.strip():
        return DiscountResult(valid=False, message="Ingen kode oppgitt")

    normalized = code.strip().upper()
    discount = db.query(DiscountCode).filter(func.upper(DiscountCode.code) == normalized).first()

    if not discount:
        return DiscountResult(valid=False, message="Ugyldig rabattkode")
    if not discount.active:
        return DiscountResult(valid=False, message="Denne rabattkoden er ikke lenger aktiv")
    if discount.expires_at and discount.expires_at < datetime.utcnow():
        return DiscountResult(valid=False, message="Denne rabattkoden har utløpt")
    if discount.max_uses is not None and discount.used_count >= discount.max_uses:
        return DiscountResult(valid=False, message="Denne rabattkoden er brukt opp")
    if discount.customer_email and (
        not customer_email or discount.customer_email.strip().lower() != customer_email.strip().lower()
    ):
        return DiscountResult(valid=False, message="Denne rabattkoden gjelder ikke denne e-postadressen")

    if discount.product_id is not None:
        applicable_items = [i for i in items if i.product_id == discount.product_id]
        if not applicable_items:
            return DiscountResult(valid=False, message="Denne rabattkoden gjelder ikke produktene i handlekurven")
    else:
        applicable_items = items

    applicable_subtotal = sum(i.price * i.quantity for i in applicable_items)

    if discount.discount_type == "percentage":
        discount_amount = applicable_subtotal * (discount.value / 100)
    else:
        discount_amount = discount.value

    # Never exceed what the discount actually applies to, and never negative
    # — protects against a fixed discount larger than the item(s) it's
    # scoped to producing a negative or nonsensical total.
    discount_amount = max(0.0, min(discount_amount, applicable_subtotal))

    return DiscountResult(
        valid=True,
        message="Rabattkode lagt til",
        discount_amount=round(discount_amount, 2),
        discount_code=discount,
    )


def try_redeem_discount_code(db: Session, discount_code_id: int) -> bool:
    """Atomically increments used_count, but only if max_uses hasn't been hit
    in the meantime. check_discount_code() above only reads — under two
    concurrent checkouts both racing the last use of a code, both reads can
    see it as valid. This does the actual, authoritative increment as a
    single conditional UPDATE, so only one of the two can win; the caller
    must reject the order if this returns False rather than trusting the
    earlier read."""

    result = db.execute(
        update(DiscountCode)
        .where(
            DiscountCode.id == discount_code_id,
            or_(DiscountCode.max_uses.is_(None), DiscountCode.used_count < DiscountCode.max_uses),
        )
        .values(used_count=DiscountCode.used_count + 1)
    )
    return result.rowcount == 1
