from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwt.exceptions import InvalidTokenError

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")  # Set a default
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY_Name = "x-api-key"

api_key_header = APIKeyHeader(name=API_KEY_Name, auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_api_key(api_key: str = Depends(api_key_header)):
    try:
        print("apie key error ", api_key)
        if api_key == os.getenv("API_KEY"):
            return api_key
        else:
            raise HTTPException(status_code=401, detail="Invalid API Key")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        return str(e)

def verify_token(token: str = Depends(auth_scheme)):  # Fix: Use correct method
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        return payload.get('id')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)
