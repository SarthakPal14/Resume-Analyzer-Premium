# Resume Analyzer — Project Viva Notes

## Problem
Students need job-specific and actionable feedback when tailoring a resume to a job description.

## Input and output
Input: PDF resume + job description.
Output: indicative match score, skill coverage, strengths, gaps, truthful bullet rewrites, action plan, interview topics and PDF report.

## Why Gemini?
The application calls Google's Gemini API through the official `google-genai` Python SDK. Google AI Studio may provide free-tier quota for eligible models and regions, but limits and availability can change.

## Why prompt chaining?
Resume extraction, job requirement extraction and comparison are separated into three focused stages. Each stage has its own system instruction and Pydantic output schema.

## Why few-shot prompting?
A sample bullet rewrite demonstrates the desired style while instructing the model not to fabricate results.

## Why rubric-based evaluation?
The weighted criteria make the assessment dimensions explicit and easier to explain and evaluate.

## Why structured output?
Pydantic schemas define expected fields and types. Gemini is asked to return JSON matching the schema, then Pydantic validates it.

## Evaluation plan
1. Test at least five resume/job-description pairs.
2. Verify extracted skills against the actual resume.
3. Check that absent terms are labelled "Not found", not assumed absent.
4. Check that bullet rewrites preserve facts.
5. Compare results with a human reviewer.
6. Record errors, revise prompts, and repeat the same test set.

## Limitations
PDF extraction can miss columns, icons and scanned text. AI can make mistakes. The match score is not an official ATS score or hiring prediction.
