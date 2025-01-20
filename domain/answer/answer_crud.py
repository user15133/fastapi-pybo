from datetime import datetime
from sqlalchemy.orm import Session
from domain.answer.answer_schema import AnswerCreate, AnswerUpdate
from models import Question, Answer, User


def create_answer(db: Session, question: Question, answer_create: AnswerCreate, user: User):
    """
    답변 생성
    """
    db_answer = Answer(
        question=question,
        content=answer_create.content,
        create_date=datetime.now(),
        user=user
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)  # 새로 생성된 객체 반환
    return db_answer


def get_answer(db: Session, answer_id: int):
    """
    답변 조회
    """
    return db.query(Answer).filter(Answer.id == answer_id).first()


def update_answer(db: Session, db_answer: Answer, answer_update: AnswerUpdate):
    """
    답변 수정
    """
    db_answer.content = answer_update.content
    db_answer.modify_date = datetime.now()
    db.add(db_answer)
    db.commit()
    return db_answer


def delete_answer(db: Session, db_answer: Answer):
    """
    답변 삭제
    """
    db.delete(db_answer)
    db.commit()


def vote_answer(db: Session, db_answer: Answer, db_user: User):
    """
    답변 추천
    """
    db_answer.voter.append(db_user)
    db.commit()
