from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import os

# تنظیمات دیتابیس
DATABASE_URL = "postgresql://hayat_user:hayat_pass_2025@localhost/hayat_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# تنظیمات امنیتی
SECRET_KEY = "hayat_secret_key_2025_very_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# مدل‌های دیتابیس
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    criteria = relationship("Criterion", back_populates="project")

class Criterion(Base):
    __tablename__ = "criteria"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    weight = Column(Float)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="criteria")

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserCreate(BaseModel):
    mobile: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    mobile: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    title: str
    description: str

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    
    class Config:
        from_attributes = True

# توابع کمکی
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="اعتبار سنجی ناموفق",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile: str = payload.get("sub")
        if mobile is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.mobile == mobile).first()
    if user is None:
        raise credentials_exception
    return user

# FastAPI App
app = FastAPI(title="Hayat AHP System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ایجاد کاربر ادمین پیش‌فرض
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    admin = db.query(User).filter(User.mobile == "09123456789").first()
    if not admin:
        admin = User(
            mobile="09123456789",
            hashed_password=get_password_hash("Admin@Hayat2025"),
            full_name="مدیر سیستم"
        )
        db.add(admin)
        db.commit()
    db.close()

# Routes
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شماره موبایل یا رمز عبور اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.mobile})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"mobile": current_user.mobile, "full_name": current_user.full_name}

@app.post("/projects/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/", response_model=List[ProjectResponse])
async def read_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@app.get("/")
async def root():
    return {"message": "Hayat AHP API v1.0", "status": "running"}
