from sqlalchemy import Column, Integer, String, Float, Boolean
from models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # Basic product info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Pricing
    price = Column(Float, nullable=False)

    # Inventory
    stock = Column(Integer, default=0)

    # Visibility
    active = Column(Boolean, default=True)

    # Optional image
    image_url = Column(String, nullable=True)
