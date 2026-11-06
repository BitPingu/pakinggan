from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

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
