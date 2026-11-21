# Resume Analyzer — Gemini Edition

**Bennett University | Prompt Engineering | Problem C9**

This Streamlit application compares a PDF resume with a job description and returns an indicative match score, skill evidence, strengths, improvement areas, bullet rewrites, recommended actions, interview preparation and a downloadable PDF report.

## UI highlights
- Redesigned, responsive dashboard: gradient hero, step cards, live input validation
- Animated match-score ring, weighted category bars, skill-evidence cards and donut chart
- Side-by-side Rewrite Studio (original vs suggested), profile chips, prompt-engineering cards
- Branded PDF report with colour-coded skill status, score bars and page footers
- **View sample report** button previews the whole dashboard without an API key
- Styles live in `assets/style.css`; theme in `.streamlit/config.toml`

## Features
- PDF resume upload and text extraction
- Job description input
- Three-stage Gemini prompt chain
- Evidence-based match estimate and weighted rubric
- Skill gap assessment
- Truthful bullet point rewriting
- Plotly dashboard and downloadable PDF report
- Prompt engineering techniques visible in the UI

## Prompt engineering techniques
1. Role prompting
2. Rubric-based evaluation
3. Few-shot prompting
4. Prompt chaining
5. Structured JSON output with Pydantic schema
6. Output format control

## Requirements
- Python 3.10+
- Google Gemini API key
- Internet connection
- Google AI Studio API access and available quota

## Windows setup (PowerShell)

1. Extract the ZIP and open the `C9_Resume_Analyzer_Gemini` folder in VS Code.
2. Create and activate a virtual environment:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
```

If Python 3.13 is unavailable, use an installed Python 3.10+ version.

3. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Create `.env`:

```powershell
Copy-Item .env.example .env
```

5. Create a Gemini API key at https://aistudio.google.com/apikey and put it in `.env`:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Do not commit `.env`, share the key, or put it in screenshots.

6. Run the app:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501.

## Run tests

```powershell
pytest -q
```

## Gemini API billing and free tier

Google AI Studio offers free-tier access for some Gemini models and regions, subject to current quotas, rate limits and availability. Free-tier access is not unlimited or guaranteed. Check current pricing and usage limits before relying on it:
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits

The app uses the official Google Gen AI Python SDK (`google-genai`) and Gemini JSON response schemas. If your selected model is not available to your API project or does not support the requested structured output, choose a supported model in `.env` after checking current model documentation.

## Pipeline
1. Resume extraction: resume text → `ResumeProfile`
2. Job extraction: job description → `JobProfile`
3. Comparison: both profiles + weighted rubric + few-shot example → `ResumeAnalysis`
4. Dashboard: Streamlit and Plotly
5. Export: ReportLab PDF

## Scoring rubric
- Required technical skills: 30%
- Relevant projects and practical evidence: 25%
- Relevant experience, internships and leadership: 20%
- Education and qualifications: 10%
- Role-specific keywords and responsibilities: 15%

The score is an AI-generated coaching estimate, not an official ATS score, hiring probability or employment decision. It must not be the sole basis for hiring decisions.

## Privacy
Resume text is sent to Google Gemini API for processing. Obtain the candidate's consent before uploading personal data. This starter app does not store uploaded resumes in a database. Review Google's current data-use terms and your university's privacy requirements before using real personal information.

## Limitations
- Scanned/image-only PDFs need OCR.
- PDF extraction can lose layout and table context.
- AI can misread evidence; verify every recommendation.
- "Not found" means not identified in the resume text, not proof that the candidate lacks the skill.
- No guarantee of ATS compatibility.


### Recommended default model
The project defaults to `gemini-3.5-flash-lite`, a stable model listed in Google's model catalogue and pricing documentation. Confirm current free-tier availability, quota and limits in AI Studio before use.


## Premium interface edition
The Streamlit interface has been redesigned with a premium SaaS-style visual system,
including a new Resume Analyzer title, dark navigation sidebar, gradient hero section,
polished upload and job-description workspace, match gauge, category charts, skill
evidence cards, rewrite studio, prompt engineering explainer and report export.
