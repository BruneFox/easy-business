from pydantic import BaseModel


class UserData(BaseModel):
    nickname: str
    email: str
    password: str
class BusinessData(BaseModel):
    name:str
class UserLogin(BaseModel):
    nickname: str
    password: str