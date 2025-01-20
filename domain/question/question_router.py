from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.question import question_schema, question_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/api/question"
)


@router.get("/list", response_model=question_schema.QuestionList)
def question_list(
    db: Session = Depends(get_db),
    page: int = Query(0, ge=0, description="페이지 번호 (0부터 시작)"),
    size: int = Query(10, gt=0, le=100, description="페이지 크기 (최대 100)"),
    keyword: str = Query("", description="검색 키워드 (기본값: 빈 문자열)")
):
    """
    페이지네이션으로 질문 데이터를 가져옵니다.
    """
    print(f"디버깅: page={page}, size={size}, keyword={keyword}")  # 디버깅 로그 추가
    total, _question_list = question_crud.get_question_list(
        db, skip=page * size, limit=size, keyword=keyword
    )
    return {
        'total': total,
        'question_list': _question_list
    }


@router.get("/detail/{question_id}", response_model=question_schema.Question)
def question_detail(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 질문의 상세 데이터를 가져옵니다.
    """
    question = question_crud.get_question(db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
    return question


@router.post("/create", status_code=status.HTTP_201_CREATED)
def question_create(
    _question_create: question_schema.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새로운 질문을 생성합니다.
    """
    print(f"디버깅: 질문 생성 요청 by user={current_user.username}")  # 디버깅 로그 추가
    question_crud.create_question(
        db=db,
        question_create=_question_create,
        user=current_user
    )
    print("디버깅: 질문 생성 완료")  # 디버깅 로그 추가


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def question_update(
    _question_update: question_schema.QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 질문을 수정합니다.
    """
    db_question = question_crud.get_question(db, question_id=_question_update.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_question.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정 권한이 없습니다.")
    question_crud.update_question(
        db=db,
        db_question=db_question,
        question_update=_question_update
    )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def question_delete(
    _question_delete: question_schema.QuestionDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 질문을 삭제합니다.
    """
    db_question = question_crud.get_question(db, question_id=_question_delete.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_question.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="삭제 권한이 없습니다.")
    question_crud.delete_question(db=db, db_question=db_question)


@router.post("/vote", status_code=status.HTTP_204_NO_CONTENT)
def question_vote(
    _question_vote: question_schema.QuestionVote,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 질문에 추천합니다.
    """
    db_question = question_crud.get_question(db, question_id=_question_vote.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="데이터를 찾을 수 없습니다.")
    question_crud.vote_question(
        db=db,
        db_question=db_question,
        db_user=current_user
    )
