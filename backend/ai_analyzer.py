"""Google Gemini API integration using JSON-schema constrained responses."""
import os
from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.schemas import ResumeProfile, JobProfile, ResumeAnalysis
from backend.prompt_templates import (
    RESUME_EXTRACTION_SYSTEM, JOB_EXTRACTION_SYSTEM, ANALYSIS_SYSTEM,
    analysis_user_prompt
)


class AIConfigurationError(RuntimeError):
    pass


def get_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        raise AIConfigurationError(
            "Gemini API key is missing. Add GEMINI_API_KEY to your .env file and restart the app."
        )
    try:
        return genai.Client(api_key=api_key)
    except Exception as exc:
        raise AIConfigurationError(f"Could not initialize Gemini client: {exc}") from exc


def _generate_structured(client, model: str, instructions: str, prompt: str, schema):
    """Generate JSON from Gemini and validate it with the Pydantic model."""
    response = client.models.generate_content(
        model=model,
        contents=f"{instructions}\n\n{prompt}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    try:
        return schema.model_validate_json(response.text)
    except ValidationError as exc:
        raise RuntimeError(
            "Gemini returned data that did not match the expected format. Please retry."
        ) from exc


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Prompt chain: resume extraction -> job extraction -> comparison."""
    if len(job_description.strip()) < 80:
        raise ValueError("Please enter a more complete job description (at least 80 characters).")
    if len(job_description) > 20000:
        raise ValueError("The job description is too long. Keep it under 20,000 characters.")

    client = get_client()
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

    resume_profile = _generate_structured(
        client, model, RESUME_EXTRACTION_SYSTEM,
        "Extract candidate information from this resume text:\n\n" + resume_text,
        ResumeProfile
    )
    job_profile = _generate_structured(
        client, model, JOB_EXTRACTION_SYSTEM,
        "Analyze this job description:\n\n" + job_description,
        JobProfile
    )
    analysis = _generate_structured(
        client, model, ANALYSIS_SYSTEM,
        analysis_user_prompt(resume_profile.model_dump(), job_profile.model_dump()),
        ResumeAnalysis
    )

    return {
        "resume_profile": resume_profile.model_dump(),
        "job_profile": job_profile.model_dump(),
        "analysis": analysis.model_dump(),
        "model": model,
    }
