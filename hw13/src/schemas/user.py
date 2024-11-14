from pydantic import constr,BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username:constr(min_length=3, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    avatar: str


    class Config:
        from_attributes = True


class RequestEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"