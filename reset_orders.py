from database import engine
from sqlalchemy import text

print("Dropping dependent tables with CASCADE...")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS payments CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS orders CASCADE;"))
    conn.commit()

print("Recreating tables from models...")

from models.order import Order, OrderItem
from models.payment import Payment

Order.__table__.create(engine, checkfirst=True)
OrderItem.__table__.create(engine, checkfirst=True)
Payment.__table__.create(engine, checkfirst=True)

print("Done resetting order-related tables.")

