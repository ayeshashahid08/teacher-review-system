from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserFullResponse
from app.services.auth_service import register_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("/add", response_model=UserFullResponse)
def add_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.designation != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add users")
    
    if user_data.designation == "admin":
        raise HTTPException(status_code=403, detail="Cannot create another admin account through this endpoint")
    
    new_user = register_user(user_data, db)
    new_user.added_by = current_user.user_id
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.designation != "admin":
        raise HTTPException(status_code=403, detail="Only admin can remove users")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.designation == "admin":
        raise HTTPException(status_code=403, detail="Cannot remove admin account")
    
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated successfully"}


# @router.get("/", response_model=list[UserResponse])
# def list_users(
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     if current_user.designation != "admin":
#         raise HTTPException(status_code=403, detail="Only admin can view all users")
    
#     users = db.query(User).filter(User.is_active == True).all()
#     return users
