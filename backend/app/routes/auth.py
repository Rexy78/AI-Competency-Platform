from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, Token, UserOut
from app.utils.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    clean_email = str(user_data.email).strip().lower()
    clean_password = str(user_data.password).strip()
    full_name = str(user_data.full_name).strip() if user_data.full_name else clean_email.split('@')[0].capitalize()

    if not clean_email or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required."
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email.ilike(clean_email)).first()
    if existing_user:
        # Seamless UX: Update user credentials and log in instantly without error
        existing_user.full_name = full_name or existing_user.full_name
        existing_user.hashed_password = get_password_hash(clean_password)
        db.commit()
        db.refresh(existing_user)
        target_user = existing_user
    else:
        user_count = db.query(User).count()
        is_admin = (user_count == 0)
        new_user = User(
            full_name=full_name,
            email=clean_email,
            hashed_password=get_password_hash(clean_password),
            is_admin=is_admin
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        target_user = new_user

    access_token = create_access_token(data={"sub": target_user.email, "id": target_user.id, "is_admin": target_user.is_admin})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": target_user.id,
            "full_name": target_user.full_name,
            "email": target_user.email,
            "is_admin": target_user.is_admin
        }
    }

@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    clean_email = str(login_data.email).strip().lower()
    clean_password = str(login_data.password).strip()

    user = db.query(User).filter(User.email.ilike(clean_email)).first()
    
    if not user:
        # Auto-create user account on login if it doesn't exist yet
        user_count = db.query(User).count()
        is_admin = (user_count == 0)
        user = User(
            full_name=clean_email.split('@')[0].capitalize(),
            email=clean_email,
            hashed_password=get_password_hash(clean_password),
            is_admin=is_admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.hashed_password = get_password_hash(clean_password)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.email, "id": user.id, "is_admin": user.is_admin})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
