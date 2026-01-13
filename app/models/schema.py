from pydantic import BaseModel , Field
from typing import List,Optional

#Schemas for user profile
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

#schema for job profile
class JDFormat(BaseModel):
    title: str = Field(description="The job title")
    company: str = Field(description="Name of the company")
    summary: str = Field(description="A comprehensive summary of the role, responsibilities, and company context (excluding the specific list of skills)")
    skills: List[str] = Field(description="A clean list of technical and soft skills required for the position")
    experience_years: Optional[int] = Field(description="Minimum years of experience required")


#schema for scoring
class SkillMatch(BaseModel):
    skill: str
    weight: int = Field(description="Importance from 1 to 5")
    matched: bool

class ScoreFormat(BaseModel):
    matches: List[SkillMatch]
    final_score: float = Field(description="Weighted match score between 0 and 1")


#Interview Schema
class Chat(BaseModel):
    question: str
    answer: str

class TopicsFormat(BaseModel):
    topics: List[str]


