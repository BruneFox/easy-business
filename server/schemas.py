from pydantic import BaseModel


class UserData(BaseModel):
    nickname: str
    email: str
    password: str
class BusinessData(BaseModel):
    name:str

class BusinessAction(BaseModel):
    id:int

class UserLogin(BaseModel):
    nickname: str
    password: str