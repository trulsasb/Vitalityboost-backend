from sqlalchemy import Column, Integer, Float, Enum
from sqlalchemy.orm import relationship
from models.base import Base

# Dette ENUM-navnet må matche databasen nøyaktig:
# "orderstatus"
ORDER_STATUS_ENUM = (
    "created",
    "processing",
    "paid",
    "failed",
    "cancelled",
    "refunded",
    "completed"
)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)

    # Koble til ENUM i databasen
    status = Column(
        Enum(
            *ORDER_STATUS_ENUM,
            name="orderstatus",   # MÅ matche databasen
            create_type=False     # Viktig: ikke prøv å lage ENUM på nytt
        ),
        nullable=False,
        default="created"
    )
