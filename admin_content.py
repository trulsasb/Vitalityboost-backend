import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.page_content import PageContent
from routers.auth import require_permission

router = APIRouter(prefix="/admin/content", tags=["Admin Content"])

_can_edit = [Depends(require_permission("can_edit_content"))]


class ContentUpdate(BaseModel):
    content: dict


@router.put("/{page}", dependencies=_can_edit)
def update_content(page: str, payload: ContentUpdate, db: Session = Depends(get_db)):
    entry = db.query(PageContent).filter(PageContent.page == page).first()
    serialized = json.dumps(payload.content)

    if entry:
        entry.content = serialized
    else:
        entry = PageContent(page=page, content=serialized)
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return {"page": entry.page, "content": json.loads(entry.content), "updated_at": entry.updated_at}
