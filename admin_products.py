from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.product import Product


router = APIRouter(prefix="/admin/products", tags=["Admin Products"])


# ---------------------------------------------------------
# INTERNAL DB HELPER
# ---------------------------------------------------------

def get_db() -> Session:
    return SessionLocal()


# ---------------------------------------------------------
# LIST ALL PRODUCTS
# ---------------------------------------------------------

@router.get("/")
def list_products():
    db = get_db()
    try:
        products = db.query(Product).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "image_url": p.image_url,
            }
            for p in products
        ]
    finally:
        db.close()


# ---------------------------------------------------------
# GET SINGLE PRODUCT
# ---------------------------------------------------------

@router.get("/{product_id}")
def get_product(product_id: int):
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "image_url": product.image_url,
        }
    finally:
        db.close()


# ---------------------------------------------------------
# CREATE PRODUCT
# ---------------------------------------------------------

@router.post("/")
def create_product(data: dict):
    db = get_db()
    try:
        product = Product(
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price"),
            image_url=data.get("image_url"),
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return {
            "created": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
            },
        }
    finally:
        db.close()


# ---------------------------------------------------------
# UPDATE PRODUCT
# ---------------------------------------------------------

@router.put("/{product_id}")
def update_product(product_id: int, data: dict):
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)
        product.price = data.get("price", product.price)
        product.image_url = data.get("image_url", product.image_url)

        db.commit()
        db.refresh(product)

        return {
            "updated": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "image_url": product.image_url,
            },
        }
    finally:
        db.close()


# ---------------------------------------------------------
# DELETE PRODUCT
# ---------------------------------------------------------

@router.delete("/{product_id}")
def delete_product(product_id: int):
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()

        return {"deleted": product_id}
    finally:
        db.close()

