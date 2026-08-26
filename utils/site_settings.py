from sqlalchemy.orm import Session

from models.site_setting import SiteSetting


def get_site_setting(db: Session, key: str) -> str | None:
    row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    return row.value if row else None


def set_site_setting(db: Session, key: str, value: str) -> None:
    row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if row:
        row.value = value
    else:
        row = SiteSetting(key=key, value=value)
        db.add(row)
    db.commit()
