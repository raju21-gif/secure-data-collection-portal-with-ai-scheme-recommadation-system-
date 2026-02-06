from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"
    image_url: str = ""
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class Feedback(BaseModel):
    name: str
    email: str
    message: str
    timestamp: str = ""

class Review(BaseModel):
    user_name: str
    user_email: str = "" # Added for ownership verification
    user_image: str = ""
    role: str = "User"
    rating: int
    comment: str
    timestamp: str = ""

class ChatMessage(BaseModel):
    user_name: str
    user_image: str = ""
    message: str
    timestamp: str = ""
    role: str = "user"
