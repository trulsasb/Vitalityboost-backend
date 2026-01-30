from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)

    # Ingen relationship til OrderItem – den modellen finnes ikke lenger
