from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from domain.answer import answer_router
from domain.question import question_router
from domain.user import user_router

# 데이터베이스 및 모델 가져오기
from database import Base, engine
from sqlalchemy.orm import Session
from models import User, Question
from datetime import datetime

# FastAPI 애플리케이션 생성
app = FastAPI()

# CORS 설정
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173"  # 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(question_router.router)
app.include_router(answer_router.router)
app.include_router(user_router.router)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))

@app.get("/")
def index():
    return FileResponse("frontend/dist/index.html")

# 애플리케이션 시작 시 데이터베이스 초기화 및 테스트 데이터 추가
@app.on_event("startup")
async def on_startup():
    """
    서버 시작 시 데이터베이스 스키마를 확인 및 생성하고, 테스트 데이터를 추가합니다.
    """
    try:
        print("초기화: 데이터베이스 스키마 생성 중...")
        Base.metadata.create_all(bind=engine)
        print("초기화 완료: 데이터베이스 스키마가 최신 상태입니다.")

        # 테스트 데이터 추가
        with Session(engine) as db:
            if db.query(User).count() == 0:
                print("테스트 데이터 추가 중...")
                user = User(username="testuser", email="test@example.com", password="testpassword")
                db.add(user)
                db.commit()
                print("테스트 사용자 추가 완료.")

            if db.query(Question).count() == 0:
                print("테스트 질문 데이터 추가 중...")
                user = db.query(User).first()
                question1 = Question(subject="테스트 질문 1", content="테스트 내용 1", create_date=datetime.now(), user=user)
                question2 = Question(subject="테스트 질문 2", content="테스트 내용 2", create_date=datetime.now(), user=user)
                db.add_all([question1, question2])
                db.commit()
                print("테스트 질문 데이터 추가 완료.")
    except Exception as e:
        print(f"초기화 실패: {e}")

# 애플리케이션 종료 시 작업
@app.on_event("shutdown")
async def on_shutdown():
    """
    서버 종료 시 필요한 작업을 처리합니다.
    """
    print("서버 종료: 정리 작업을 수행합니다.")

# 기본 루트 확인용 엔드포인트
@app.get("/")
def read_root():
    """
    기본 루트 엔드포인트로 상태를 확인합니다.
    """
    return {"message": "FastAPI 서버가 실행 중입니다!"}

# 디버그용: 잘못된 경로 처리
@app.get("/{full_path:path}")
def handle_404(full_path: str):
    """
    잘못된 경로를 요청한 경우 404 메시지 반환
    """
    return {"error": "잘못된 경로 요청", "path": full_path}
