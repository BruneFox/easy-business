from pydantic import BaseModel,ConfigDict, Field

class ChangeMoney(BaseModel):
    cash: int

class UserData(BaseModel):
    nickname: str
    email: str
    password: str

class BusinessData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=50)


class UserLogin(BaseModel):
    nickname: str
    password: str