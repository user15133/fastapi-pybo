from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.answer import answer_schema, answer_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/api/answer",
)

@router.get("/list", response_model=answer_schema.AnswerList)
def answer_list(
    db: Session = Depends(get_db),
    page: int = Query(0, ge=0, description="페이지 번호 (0부터 시작)"),
    size: int = Query(10, gt=0, le=100, description="페이지 크기 (최대 100)")
):
    total, _answer_list = answer_crud.get_answer_list(
        db, skip=page * size, limit=size
    )
    return {
        'total': total,
        'answer_list': _answer_list
    }

@router.post("/create", status_code=status.HTTP_201_CREATED)
def answer_create(
    _answer_create: answer_schema.AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    answer_crud.create_answer(
        db=db,
        answer_create=_answer_create,
        user=current_user
    )

@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def answer_update(
    _answer_update: answer_schema.AnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_update.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다.")
    answer_crud.update_answer(db=db, db_answer=db_answer, answer_update=_answer_update)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def answer_delete(
    _answer_delete: answer_schema.AnswerDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_delete.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다.")
    answer_crud.delete_answer(db=db, db_answer=db_answer)

@router.post("/vote", status_code=status.HTTP_204_NO_CONTENT)
def answer_vote(
    _answer_vote: answer_schema.AnswerVote,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_vote.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    answer_crud.vote_answer(db, db_answer=db_answer, db_user=current_user)
