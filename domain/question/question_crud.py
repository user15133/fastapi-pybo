from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from domain.question.question_schema import QuestionCreate, QuestionUpdate
from sqlalchemy import or_
from models import Question, User, Answer


def get_question_list(db: Session, skip: int = 0, limit: int = 10, keyword: str = ""):
    """
    질문 리스트 조회
    """
    question_query = db.query(Question).options(
        joinedload(Question.answers),  # 답변 관계 로딩
        joinedload(Question.voter)    # 추천 관계 로딩
    )

    if keyword:
        search = f"%{keyword}%"
        question_query = question_query.filter(
            or_(
                Question.subject.ilike(search),  # 제목 검색
                Question.content.ilike(search),  # 내용 검색
                Question.user.has(User.username.ilike(search))  # 작성자 검색
            )
        )

    total = question_query.count()
    questions = question_query.order_by(Question.create_date.desc()).offset(skip).limit(limit).all()

    return total, questions


def get_question(db: Session, question_id: int):
    """
    질문 상세 조회
    """
    return db.query(Question).options(
        joinedload(Question.answers),
        joinedload(Question.voter)
    ).filter(Question.id == question_id).first()


def create_question(db: Session, question_create: QuestionCreate, user: User):
    """
    질문 생성
    """
    db_question = Question(
        subject=question_create.subject,
        content=question_create.content,
        create_date=datetime.now(),
        user=user
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def update_question(db: Session, db_question: Question, question_update: QuestionUpdate):
    """
    질문 수정
    """
    db_question.subject = question_update.subject
    db_question.content = question_update.content
    db_question.modify_date = datetime.now()
    db.add(db_question)
    db.commit()
    return db_question


def delete_question(db: Session, db_question: Question):
    """
    질문 삭제
    """
    db.delete(db_question)
    db.commit()


def vote_question(db: Session, db_question: Question, db_user: User):
    """
    질문 추천
    """
    db_question.voter.append(db_user)
    db.commit()
