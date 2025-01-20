from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    """
    사용자 생성
    """
    db_user = User(
        username=user_create.username,
        password=pwd_context.hash(user_create.password1),
        email=user_create.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_existing_user(db: Session, user_create: UserCreate):
    """
    사용자 존재 여부 확인
    """
    return db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()


def get_user(db: Session, username: str):
    """
    사용자 조회
    """
    return db.query(User).filter(User.username == username).first()
