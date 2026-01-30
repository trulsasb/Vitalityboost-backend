from sqlalchemy import Column, Integer, Float, Enum
from models.base import Base

ORDER_STATUS_ENUM = (
    "PENDING_PAYMENT",
    "AUTHORIZED",
    "PAID",
    "FAILED",
    "REFUNDED"
)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)

    status = Column(
        Enum(
            *ORDER_STATUS_ENUM,
            name="orderstatus",
            create_type=False
        ),
        nullable=False,
        default="PENDING_PAYMENT"
    )
