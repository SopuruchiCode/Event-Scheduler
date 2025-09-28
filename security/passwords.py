from passlib.context import CryptContext


pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw_pwd: str) -> str:
    return pwd_cxt.hash(raw_pwd)

def verify_password(raw_pwd: str, hashed_pwd: str) -> bool:
    return pwd_cxt.verify(raw_pwd, hashed_pwd)