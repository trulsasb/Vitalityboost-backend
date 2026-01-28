from database import Base, engine
from models.order import Order, OrderItem

print("Dropping order tables...")
OrderItem.__table__.drop(engine, checkfirst=True)
Order.__table__.drop(engine, checkfirst=True)

print("Creating order tables...")
Order.__table__.create(engine, checkfirst=True)
OrderItem.__table__.create(engine, checkfirst=True)

print("Done.")
