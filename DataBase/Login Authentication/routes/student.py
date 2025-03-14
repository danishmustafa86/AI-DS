from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.student import Student
from utils.utils_helper import create_access_token, verify_token as decode_access_token, verify_password, hash_password
from validations.validations import StudentCreate, LoginStudent
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordBearer

# Fix: Define OAuth2 scheme properly
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Student.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = APIRouter()

@app.get("/")
def read_root():
    return {"Hello": "Server is running at student page when you open the browser"}

def verify_token(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)  # Correct function call
    if isinstance(payload, str):
        raise HTTPException(status_code=401, detail=payload)
    return payload

@app.get("/me")
def read_users_me(user: dict = Depends(verify_token)):
    return {
        "token": user,
        "message": "You are authorized to view this page"
    }

@app.post("/register")
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = hash_password(student.password)
        db_student = Student(
            ag=student.ag,
            name=student.name,
            fullname=student.fullname,
            password=hashed_password,  # Ensure password is hashed
            degree=student.degree,
            email=student.email
        )
        db.add(db_student)
        try:
            db.commit()
            db.refresh(db_student)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Email already exists")

        token = create_access_token(data={"sub": db_student.email, "id": db_student.ag, "role": "student", "name": db_student.name})

        return {
            "message": "Student registered successfully",
            "access_token": token,
            "status": 200
        }

    except Exception as e:
        return {
            "message": "An error occurred",
            "status": 400,
            "error": str(e)
        }

@app.post("/login")
def login_student(student: LoginStudent, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.email == student.email).first()
    if db_student is None or not verify_password(student.password, db_student.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_student.email, "id": db_student.ag, "role": "student", "name": db_student.name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "status": 200
    }

@app.get("/students/{id}")  # Fix: Avoid conflict with "/me"
def get_student(id: int, token:str = Depends(verify_token) , db: Session = Depends(get_db)):
    payload = verify_token(token)
    if isinstance(payload, str):
        raise HTTPException(status_code=401, detail=payload)

    student = db.query(Student).filter(Student.ag == id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{id}")
def update_student(id: int, student: StudentCreate, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if isinstance(payload, str):
        raise HTTPException(status_code=401, detail=payload)

    db_student = db.query(Student).filter(Student.ag == id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db_student.name = student.name
    db_student.fullname = student.fullname
    db_student.password = hash_password(student.password)
    db_student.degree = student.degree
    db_student.email = student.email

    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/students/{id}")
def delete_student(id: int,  token: str = Depends(verify_token) ,db: Session = Depends(get_db)):
    payload = verify_token(token)
    if isinstance(payload, str):
        raise HTTPException(status_code=401, detail=payload)

    db_student = db.query(Student).filter(Student.ag == id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted"}