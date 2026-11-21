"""Pydantic schemas for predictable, validated Gemini responses."""
from pydantic import BaseModel, Field


class ResumeProfile(BaseModel):
    candidate_name: str = Field(description="Name if clearly present; otherwise Unknown")
    headline: str = Field(description="Short professional headline supported by resume evidence")
    skills: list[str]
    education: list[str]
    experience: list[str]
    projects: list[str]
    achievements: list[str]
    evidence_notes: list[str]


class JobProfile(BaseModel):
    role_title: str
    seniority: str
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    qualifications: list[str]
    keywords: list[str]


class SkillAssessment(BaseModel):
    skill: str
    status: str = Field(description="One of: Strong evidence, Partial evidence, Not found")
    evidence: str
    importance: str = Field(description="One of: High, Medium, Low")


class CategoryScore(BaseModel):
    category: str
    score: int = Field(ge=0, le=100)
    weight_percent: int = Field(ge=0, le=100)
    rationale: str


class BulletRewrite(BaseModel):
    original: str
    improved: str
    rationale: str
    evidence_warning: str


class ResumeAnalysis(BaseModel):
    match_score: int = Field(ge=0, le=100)
    match_summary: str
    strengths: list[str]
    improvement_areas: list[str]
    skill_assessments: list[SkillAssessment]
    category_scores: list[CategoryScore]
    rewritten_bullets: list[BulletRewrite]
    recommended_actions: list[str]
    interview_preparation: list[str]
    fairness_note: str
