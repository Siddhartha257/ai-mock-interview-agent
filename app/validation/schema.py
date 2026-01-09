from pydantic import BaseModel
from typing import List,Optional

class Work(BaseModel):
    company: str
    duration: str
    description: List[str]

class Projects(BaseModel):
    title: str
    description: List[str]
    link: Optional[str]

class Education(BaseModel):
    degree: str
    college: str
    year: Optional[str]  
    cgpa: Optional[str]  

class Profile(BaseModel):
    name: str
    gmail: str
    summary: str
    work_experience: List[Work]
    projects: List[Projects]
    skills: List[str]
    certifications: List[str]
    education: List[Education]

