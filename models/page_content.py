from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from models.base import Base


class PageContent(Base):
    __tablename__ = "page_content"

    id = Column(Integer, primary_key=True, index=True)
    page = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
