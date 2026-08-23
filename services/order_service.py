from sqlalchemy.orm import Session

from models.discount import DiscountCode, DiscountRedemption
from models.order import Order, OrderStatus
from models.product import Product


def release_failed_order(db: Session, order_id: int) -> None:
    """Undo the stock/discount reservations made at order-creation time when
    a payment never completes (webhook reports failure, expiry, or
    cancellation).

    Order creation reserves stock and a discount-code use immediately, before
    payment is confirmed (see routers/orders.py), so this is the single place
    both payment webhooks call to release that reservation. Guarded on
    PENDING_PAYMENT so a duplicate webhook delivery — which Stripe/Vipps both
    explicitly don't guarantee against — can't restore stock twice.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.status != OrderStatus.PENDING_PAYMENT:
        return

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    redemption = (
        db.query(DiscountRedemption)
        .filter(DiscountRedemption.order_id == order_id)
        .first()
    )
    if redemption:
        discount = (
            db.query(DiscountCode)
            .filter(DiscountCode.id == redemption.discount_code_id)
            .first()
        )
        if discount and discount.used_count > 0:
            discount.used_count -= 1
        db.delete(redemption)

    order.status = OrderStatus.CANCELLED
