import datetime
from pydantic import BaseModel, field_validator
from domain.user.user_schema import User

# 기본 Answer 스키마
class Answer(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
    user: User | None
    question_id: int
    modify_date: datetime.datetime | None = None
    voter: list[User] = []

    class Config:
        from_attributes = True

# 답변 생성 스키마
class AnswerCreate(BaseModel):
    content: str
    question_id: int

    @field_validator("content")
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

# 답변 목록 스키마
class AnswerList(BaseModel):
    total: int = 0
    answer_list: list[Answer] = []

# 답변 수정 스키마
class AnswerUpdate(AnswerCreate):
    answer_id: int

# 답변 삭제 스키마
class AnswerDelete(BaseModel):
    answer_id: int

# 답변 추천 스키마
class AnswerVote(BaseModel):
    answer_id: int
