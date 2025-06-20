# crud/user_crud.py
from sqlalchemy.orm import Session
from backend.app.models.schemas.user import UserCreate, User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        password_hash=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
