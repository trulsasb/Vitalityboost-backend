from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


# ---------------------------------------------------------
# STATIC USER LIST
# ---------------------------------------------------------

USERS = [
    {"id": 1, "name": "Truls"},
    {"id": 2, "name": "Kirsti"},
]


# ---------------------------------------------------------
# LIST USERS
# ---------------------------------------------------------

@router.get("/")
def list_users():
    return USERS


# ---------------------------------------------------------
# GET SINGLE USER
# ---------------------------------------------------------

@router.get("/{user_id}")
def get_user(user_id: int):
    for user in USERS:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


# ---------------------------------------------------------
# ADD USER
# ---------------------------------------------------------

@router.post("/")
def add_user(data: dict):
    name = data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Missing 'name'")

    new_id = max([u["id"] for u in USERS]) + 1 if USERS else 1
    new_user = {"id": new_id, "name": name}
    USERS.append(new_user)

    return {"created": True, "user": new_user}


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------

@router.delete("/{user_id}")
def delete_user(user_id: int):
    for user in USERS:
        if user["id"] == user_id:
            USERS.remove(user)
            return {"deleted": user_id}
    raise HTTPException(status_code=404, detail="User not found")
