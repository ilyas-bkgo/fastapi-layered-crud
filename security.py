import bcrypt
import jwt
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# jwt constants
SECRET_KEY = "super-secret-key-change-at-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def hash_password(password: str) -> str:
    # 1. Convert the plain text string to bytes
    pwd_bytes = password.encode("utf-8")
    # 2. generate a random salt and mix it with the pws bytes
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    # 3. decode the bytes string back into python string for sqlite storage
    return hashed_pwd.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# token interceptor dependency

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
   credentials_exception = HTTPException(
       status_code = status.HTTP_401_UNAUTHORIZED,
       detail="could not validate credentials",
       headers={"WWW-Authenticate": "Bearer"},
   )

   try:
       payload:dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

       username: str | None = payload.get("sub")
       user_id: int | None = payload.get("user_id")

       if username is None or user_id is None:
           raise credentials_exception

       return {"id": user_id, "username": username}



   except jwt.ExpiredSignatureError:
       raise HTTPException(
           status_code= status.HTTP_401_UNAUTHORIZED,
           detail="token has expired",
           headers={"WWW-Authenticate": "Bearer"},
       )

   except jwt.InvalidTokenError:
      raise credentials_exception
