from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import register_user, authenticate_user, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import PasswordChange
router = APIRouter(prefix="/auth", tags=["Auth"])



# @router.post("/register", response_model=UserResponse)
# def register(
#     user_data: UserCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     if current_user.designation != "admin":
#         raise HTTPException(status_code=403, detail="Only admin can register new users")
#     new_user = register_user(user_data, db)
#     return new_user

@router.post("/change-password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    
    current_user.password_hash = hash_password(data.new_password)
    current_user.must_change_password = False
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/reset-password/{user_id}")
def reset_password(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.designation != "admin":
        raise HTTPException(status_code=403, detail="Only admin can reset passwords")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    default_password = "KKAMHS123!"
    user.password_hash = hash_password(default_password)
    user.must_change_password = True
    db.commit()
    return {"message": f"Password reset to default. User must change it on next login."}



@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    access_token = create_access_token(data={
        "user_id": user.user_id,
        "role": user.designation,
        "must_change_password": user.must_change_password
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
        "designation": user.designation
    }
