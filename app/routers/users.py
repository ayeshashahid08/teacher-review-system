from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserFullResponse, UserUpdate
from app.services.auth_service import register_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("/add", response_model=UserFullResponse)
def add_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.designation not in [ "admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin and principal can add users")
    
    if user_data.designation == "admin":
        raise HTTPException(status_code=403, detail="Cannot create another admin account through this endpoint")

    principal_is_active = db.query(User).filter(User.designation == "principal", User.is_active == True)
    if principal_is_active and user_data.designation == "principal":
        raise HTTPException(status_code = 403, detail= "A principal already exists")
    
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
    if current_user.designation not in [ "admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin and principal can add users")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.designation == "admin":
        raise HTTPException(status_code=403, detail="Cannot remove admin account")
    
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated successfully"}


@router.put("/edit/{user_id}", response_model=UserFullResponse)
def edit_user(
    user_id: int,
    user_data: UserUpdate,  
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.designation not in [ "admin", "principal"]:
        raise HTTPException(status_code=403, detail="Only admin and principal can add users")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    if user_data.designation == "principal":
        existing_principal = db.query(User).filter(
            User.designation == "principal",
            User.is_active == True,
            User.user_id != user_id
        ).first()
        if existing_principal:
            raise HTTPException(status_code=403, detail="A principal already exists")

    # Prevent changing to admin
    if user_data.designation == "admin":
        raise HTTPException(status_code=403, detail="Cannot assign admin role")

    # Update fields dynamically
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user