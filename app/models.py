from pydantic import BaseModel,EmailStr
from typing import Optional

class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

class TeamMember(BaseModel):
    email: EmailStr
    given_name: str  # First name
    family_name: str  # Last name
    
class Task(BaseModel):
    task_id:Optional[str] = None 
    title: str
    description: str
    assigned_to: Optional[str] = None   # team member's email or username
    deadline: str     # or DateTime type
    task_status:str #active/inactive
    created_at:str
    