import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.page_content import PageContent

router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/{page}")
def get_content(page: str, db: Session = Depends(get_db)):
    entry = db.query(PageContent).filter(PageContent.page == page).first()
    if not entry:
        raise HTTPException(status_code=404, detail="No saved content for this page")
    return {"page": entry.page, "content": json.loads(entry.content), "updated_at": entry.updated_at}
