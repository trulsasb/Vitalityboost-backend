from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------------------------------------------------
# PUBLIC PRODUCT LISTING
# ---------------------------------------------------------

@router.get("/")
def list_products(db: Session = Depends(get_db)):
    """
    Return only active products.
    This is the customer-facing product list.
    """
    return (
        db.query(Product)
        .filter(Product.active == True)
        .order_by(Product.id.desc())
        .all()
    )


# ---------------------------------------------------------
# PUBLIC PRODUCT DETAIL
# ---------------------------------------------------------

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Return a single product by ID.
    Only active products are visible to customers.
    """
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.active == True)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
