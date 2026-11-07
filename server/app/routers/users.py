from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

# user endpoints
router = APIRouter(prefix="/api/users", tags=["Users"])


# accept registration details
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )

    # check whether the username or email is already registered
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    db_user = User(
        username=user.username,
        email=str(user.email),
        # hash the password
        hashed_password=hash_password(user.password),
    )

    # save the new user to postgresql
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # return the created user's public info
    return db_user


# login endpoint
@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    # verify the submitted password against the stored hash
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # generate a jwt using the user's database id
    access_token = create_access_token(subject=str(db_user.id))

    # return the access token
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# let a logged-in user retrieve their own profile using their access token
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
