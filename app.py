import html
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st
import plotly.graph_objects as go

from backend.resume_parser import extract_resume_text, ResumeParseError
from backend.ai_analyzer import analyze_resume, AIConfigurationError
from backend.prompt_templates import (
    RESUME_EXTRACTION_SYSTEM, JOB_EXTRACTION_SYSTEM, ANALYSIS_SYSTEM,
    RUBRIC, FEW_SHOT_EXAMPLE
)
from utils.report_generator import build_pdf_report
from utils.demo_data import get_demo_result

load_dotenv()

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- styling
CSS_PATH = Path(__file__).parent / "assets" / "style.css"
st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

ICONS = {
    "logo": '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="m9 15 2 2 4-4"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    "alert": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8v5M12 17h.01"/></svg>',
    "help": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 9a2.5 2.5 0 1 1 3.6 2.2c-.8.5-1.1 1-1.1 1.8M12 17h.01"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>',
    "layers": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/></svg>',
    "trend": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>',
    "list": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6h12M9 12h12M9 18h12M4 6h.01M4 12h.01M4 18h.01"/></svg>',
    "info": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
}


def esc(value) -> str:
    return html.escape(str(value or ""))


def H(markup: str) -> str:
    """Collapse indentation/newlines so Markdown never treats the HTML as a code block."""
    return " ".join(line.strip() for line in markup.strip().splitlines())


def render(markup: str):
    st.markdown(H(markup), unsafe_allow_html=True)


def section_heading(kicker, title, subtitle=""):
    sub = f'<div class="sub">{esc(subtitle)}</div>' if subtitle else ""
    render(f'<div class="sec"><div class="eyebrow">{esc(kicker)}</div><div class="title">{esc(title)}</div>{sub}</div>')


def score_label(score):
    if score >= 80:
        return "Strong alignment", "good", "#1fb582"
    if score >= 60:
        return "Promising match", "partial", "#e9a62f"
    return "Needs improvement", "missing", "#e0606f"


def bar_class(score):
    return "f-good" if score >= 75 else ("f-mid" if score >= 55 else "f-low")


def icon_list(items, kind="good", empty="Nothing to show yet."):
    if not items:
        return f'<div class="empty">{esc(empty)}</div>'
    rows = []
    for i, item in enumerate(items, 1):
        if kind == "good":
            mk = f'<span class="mk mk-good">{ICONS["check"]}</span>'
        elif kind == "warn":
            mk = f'<span class="mk mk-warn">{ICONS["alert"]}</span>'
        elif kind == "q":
            mk = f'<span class="mk mk-q">{ICONS["help"]}</span>'
        else:
            mk = f'<span class="mk mk-num">{i}</span>'
        rows.append(f"<li>{mk}<span>{esc(item)}</span></li>")
    return f'<ul class="ilist">{"".join(rows)}</ul>'


def panel(title, body, subtitle="", dot=None):
    dot_html = f'<span class="dot" style="background:{dot}"></span>' if dot else ""
    sub = f'<div class="panel-s">{esc(subtitle)}</div>' if subtitle else '<div style="height:10px"></div>'
    return f'<div class="panel"><div class="panel-h">{dot_html}{esc(title)}</div>{sub}{body}</div>'


def chips(items, alt=False):
    if not items:
        return '<div class="empty">Not identified.</div>'
    cls = "chip alt" if alt else "chip"
    return '<div class="chips">' + "".join(f'<span class="{cls}">{esc(i)}</span>' for i in items) + "</div>"


def plain_list(items):
    if not items:
        return '<div class="empty">Not identified.</div>'
    return '<ul class="plain">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def score_ring(score, color):
    r, c = 80, 2 * 3.14159265 * 80
    offset = c * (1 - max(0, min(score, 100)) / 100)
    return (
        '<div class="ring"><svg viewBox="0 0 190 190">'
        f'<circle class="rtrack" cx="95" cy="95" r="{r}" fill="none" stroke-width="14"/>'
        f'<circle class="val" cx="95" cy="95" r="{r}" fill="none" stroke="{color}" stroke-width="14" '
        f'stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{offset:.1f}"/></svg>'
        f'<div class="center"><div class="num">{score}</div><div class="of">out of 100</div></div></div>'
    )


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    rubric_items = [
        ("Technical skills", 30), ("Projects & practical work", 25), ("Relevant experience", 20),
        ("Role alignment", 15), ("Education", 10),
    ]
    rubric_html = "".join(
        f'<div class="sb-rubric"><span class="lbl">{l}</span><span class="bar"><i style="width:{w * 3}%"></i></span><b>{w}%</b></div>'
        for l, w in rubric_items
    )
    render(f"""
    <div class="sb-brand"><div class="sb-logo">{ICONS["logo"]}</div>
      <div><div class="sb-name">Resume Analyzer</div><div class="sb-tag">AI career toolkit</div></div></div>
    <div class="sb-title">How it works</div>
    <ul class="sb-steps">
      <li><span class="n">1</span><span>Upload your resume as a PDF</span></li>
      <li><span class="n">2</span><span>Paste the target job description</span></li>
      <li><span class="n">3</span><span>Review your match and skill gaps</span></li>
      <li><span class="n">4</span><span>Improve bullets and export the report</span></li>
    </ul>
    <div class="sb-title">Evaluation framework</div>
    {rubric_html}
    <div class="sb-foot"><b>Powered by Google Gemini.</b><br>Feedback is advisory. Always verify suggestions against your real experience.</div>
    """)

# ---------------------------------------------------------------- hero
render(f"""
<div class="hero">
  <span class="hero-kicker"><i></i>AI-powered resume insights</span>
  <h1>Turn your resume into a <span>stronger application</span></h1>
  <p>See how your experience aligns with the role, uncover skill gaps, and get truthful, evidence-based
  suggestions to improve every bullet.</p>
  <div class="hero-feats">
    <span class="hero-feat"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/></svg>Weighted match score</span>
    <span class="hero-feat"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>Evidence-based skill check</span>
    <span class="hero-feat"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>Bullet rewrite studio</span>
    <span class="hero-feat"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0-4-4m4 4 4-4M5 21h14"/></svg>PDF report export</span>
  </div>
</div>
""")

# ---------------------------------------------------------------- inputs
section_heading("Start here", "Build your analysis", "Add your resume and the role you want. We handle the comparison.")
col_resume, col_job = st.columns([0.9, 1.1], gap="large")

with col_resume:
    with st.container(key="card_resume"):
        render('<div class="card-head"><span class="card-num">1</span><span class="card-title">Your resume</span></div>'
               '<div class="card-sub">Upload a PDF to extract your skills, experience and projects.</div>')
        uploaded_file = st.file_uploader(
            "Resume PDF", type=["pdf"], label_visibility="collapsed",
            help="PDF only · Maximum 10 MB · Text-based PDFs work best",
        )
        if uploaded_file:
            render(f'<div class="field-meta"><span class="ok">✓ Ready · {uploaded_file.size / 1024:.0f} KB</span></div>')
        else:
            render('<div class="field-meta"><span>PDF · up to 10 MB · text-based files recommended</span></div>')

with col_job:
    with st.container(key="card_job"):
        render('<div class="card-head"><span class="card-num">2</span><span class="card-title">Target job description</span></div>'
               '<div class="card-sub">Paste the responsibilities, required skills and qualifications.</div>')
        job_description = st.text_area(
            "Job description", height=170, label_visibility="collapsed",
            placeholder="Paste the job title, responsibilities, required skills and qualifications…",
        )
        n = len(job_description.strip())
        status = (f'<span class="ok">✓ {n:,} characters</span>' if n >= 80
                  else f'<span>Add at least 80 characters ({n} so far)</span>')
        render(f'<div class="field-meta">{status}<span>Max 20,000</span></div>')

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
run_col, demo_col, hint_col = st.columns([0.9, 0.7, 1.4], vertical_alignment="center", gap="medium")
with run_col:
    analyze_clicked = st.button("✦  Analyze my resume", type="primary", use_container_width=True)
with demo_col:
    demo_clicked = st.button("View sample report", use_container_width=True,
                             help="Preview the dashboard with example data (no API key needed).")
with hint_col:
    render(f'<div class="run-hint">{ICONS["lock"]}'
           'Your PDF is processed in memory and is not stored by this app.</div>')

if demo_clicked:
    st.session_state.analysis_result = get_demo_result()

if analyze_clicked:
    if uploaded_file is None:
        st.error("Please upload your resume PDF to continue.")
    elif len(job_description.strip()) < 80:
        st.error("Please paste a more complete job description (at least 80 characters).")
    else:
        try:
            with st.spinner("Reviewing your resume and matching it against the role…"):
                resume_text = extract_resume_text(uploaded_file.getvalue())
                st.session_state.analysis_result = analyze_resume(resume_text, job_description)
            st.toast("Your analysis is ready.", icon="✅")
        except ResumeParseError as exc:
            st.error(str(exc))
        except AIConfigurationError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Analysis could not be completed: {exc}")
            st.caption("Check your Gemini API key, model availability, internet connection and API quota.")

result = st.session_state.get("analysis_result")

# ---------------------------------------------------------------- empty state
if not result:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    section_heading("What you'll get", "A complete picture in one report")
    cards = [
        ("target", "ic-blue", "Match score", "A weighted 0-100 estimate across skills, projects, experience, education and role fit."),
        ("layers", "ic-green", "Skill evidence", "Every required skill marked as strong, partial or not found, with the proof from your resume."),
        ("trend", "ic-violet", "Truthful rewrites", "Sharper bullet points that never invent achievements, plus an action plan and interview prep."),
    ]
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, (ic, cls, t, d) in zip((c1, c2, c3), cards):
        with col:
            render(f'<div class="kpi" style="align-items:flex-start;height:100%"><div class="ic {cls}">{ICONS[ic]}</div>'
                   f'<div><div style="font-weight:700;color:var(--ink);font-size:.98rem">{t}</div>'
                   f'<div class="l" style="line-height:1.55;font-size:.84rem">{d}</div></div></div>')

# ---------------------------------------------------------------- results
if result:
    analysis = result["analysis"]
    resume = result["resume_profile"]
    job = result["job_profile"]
    score = int(analysis.get("match_score", 0))
    label, label_cls, ring_color = score_label(score)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    meta = f"{resume.get('candidate_name', 'Candidate')} · {job.get('role_title', 'Target role')}"
    if result.get("model") == "demo-data":
        meta += " · Sample data"
    section_heading("Your results", "Resume insights", meta)

    kpis = [
        ("target", "ic-blue", f"{score}<small>/100</small>", "Overall match"),
        ("layers", "ic-violet", str(len(analysis.get("skill_assessments", []))), "Skills reviewed"),
        ("check", "ic-green", str(len(analysis.get("strengths", []))), "Strengths found"),
        ("list", "ic-amber", str(len(analysis.get("recommended_actions", []))), "Action items"),
    ]
    render('<div class="kpis">' + "".join(
        f'<div class="kpi"><div class="ic {cls}">{ICONS[ic]}</div><div><div class="v">{v}</div><div class="l">{l}</div></div></div>'
        for ic, cls, v, l in kpis) + "</div>")

    left, right = st.columns([0.8, 1.2], gap="large")
    with left:
        render(f"""
        <div class="panel"><div class="score-wrap">
          <div class="panel-h" style="align-self:flex-start">Match overview</div>
          {score_ring(score, ring_color)}
          <span class="badge {label_cls}">{esc(label)}</span>
        </div>
        <div class="score-sum">{esc(analysis.get("match_summary", ""))}</div></div>
        """)
    with right:
        cats = analysis.get("category_scores", [])
        if cats:
            rows = "".join(
                f'<div class="cat"><div class="cat-top"><span><span class="cat-name">{esc(c.get("category"))}</span>'
                f'<span class="cat-w">{int(c.get("weight_percent", 0))}% weight</span></span>'
                f'<span class="cat-score">{int(c.get("score", 0))}<small>/100</small></span></div>'
                f'<div class="track"><div class="fill {bar_class(int(c.get("score", 0)))}" style="width:{int(c.get("score", 0))}%"></div></div>'
                f'<div class="cat-why">{esc(c.get("rationale"))}</div></div>'
                for c in cats)
        else:
            rows = '<div class="empty">No category scores were returned.</div>'
        render(panel("Category breakdown", rows, "How your profile aligns across the evaluation criteria."))

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    tab_overview, tab_skills, tab_rewrite, tab_profile, tab_prompts = st.tabs(
        ["Overview", "Skills analysis", "Rewrite studio", "Profile details", "Prompt engineering"])

    # ---- Overview
    with tab_overview:
        a, b = st.columns(2, gap="large")
        with a:
            render(panel("Your strengths", icon_list(analysis.get("strengths"), "good"), dot="#27b383"))
        with b:
            render(panel("Areas to improve", icon_list(analysis.get("improvement_areas"), "warn"), dot="#e9a62f"))
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        a, b = st.columns(2, gap="large")
        with a:
            render(panel("Next best actions", icon_list(analysis.get("recommended_actions"), "num"), dot="#2f5bea"))
        with b:
            render(panel("Interview preparation", icon_list(analysis.get("interview_preparation"), "q"), dot="#6a49d6"))

    # ---- Skills
    with tab_skills:
        section_heading("Skill coverage", "Where you stand",
                        "Evidence is based on what appears in the resume text, not assumptions about your abilities.")
        assessments = analysis.get("skill_assessments", [])
        if assessments:
            def bucket(s):
                return "good" if s == "Strong evidence" else ("partial" if s == "Partial evidence" else "missing")
            counts = {"good": 0, "partial": 0, "missing": 0}
            for it in assessments:
                counts[bucket(it.get("status"))] += 1

            chart_col, grid_col = st.columns([0.7, 1.5], gap="large")
            with chart_col:
                fig = go.Figure(go.Pie(
                    labels=["Strong evidence", "Partial evidence", "Not found"],
                    values=[counts["good"], counts["partial"], counts["missing"]],
                    hole=.72, sort=False, textinfo="none", direction="clockwise",
                    marker=dict(colors=["#27b383", "#eaa832", "#e0606f"], line=dict(color="#fff", width=3)),
                    hovertemplate="%{label}: %{value}<extra></extra>",
                ))
                fig.update_layout(
                    height=250, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    annotations=[dict(text=f"<b>{len(assessments)}</b><br><span style='font-size:12px;color:#7a889e'>skills</span>",
                                      showarrow=False, font=dict(size=30, family="Plus Jakarta Sans, Inter, Arial, sans-serif", color="#16233b"))],
                )
                with st.container(key="card_donut"):
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    render(f"""
                    <div class="legend" style="flex-direction:column;gap:9px">
                      <span><i style="background:#27b383"></i>Strong evidence · <b>{counts["good"]}</b></span>
                      <span><i style="background:#eaa832"></i>Partial evidence · <b>{counts["partial"]}</b></span>
                      <span><i style="background:#e0606f"></i>Not found · <b>{counts["missing"]}</b></span>
                    </div>""")
            with grid_col:
                cards_html = []
                for it in assessments:
                    bk = bucket(it.get("status"))
                    cards_html.append(
                        f'<div class="skill s-{bk}"><div class="skill-top"><span class="skill-name">{esc(it.get("skill"))}</span>'
                        f'<span class="badge {bk}">{esc(it.get("status"))}</span></div>'
                        f'<div class="skill-ev">{esc(it.get("evidence"))}</div>'
                        f'<span class="skill-imp">{esc(it.get("importance"))} importance</span></div>')
                render('<div class="skills">' + "".join(cards_html) + "</div>")
            render(f'<div class="note">{ICONS["info"]}<div><b>Marked "Not found"?</b> The skill may still be part of your experience, '
                   'it just was not identified in the resume text. Add it only if you genuinely have it.</div></div>')
        else:
            st.info("No skill assessments were returned.")

    # ---- Rewrite studio
    with tab_rewrite:
        section_heading("Resume polish", "Rewrite studio",
                        "Make your experience clearer and more impactful without inventing achievements.")
        rewrites = analysis.get("rewritten_bullets", [])
        if rewrites:
            for i, item in enumerate(rewrites, 1):
                warn = (f'<div class="rw-warn">{ICONS["alert"]}<span>{esc(item.get("evidence_warning"))}</span></div>'
                        if item.get("evidence_warning") else "")
                why = (f'<div class="rw-foot"><b>Why it works:</b> {esc(item.get("rationale"))}</div>'
                       if item.get("rationale") else "")
                render(f"""
                <div class="rw"><div class="rw-grid">
                  <div class="rw-col before"><div class="rw-lbl">Original · #{i}</div><div class="rw-txt">{esc(item.get("original"))}</div></div>
                  <div class="rw-col after"><div class="rw-lbl">✦ Suggested version</div><div class="rw-txt">{esc(item.get("improved"))}</div></div>
                </div>{why}{warn}</div>""")
        else:
            st.info("No bullet rewrites were suggested for this resume.")
        st.caption("Always verify that each rewritten bullet accurately reflects your actual work.")

    # ---- Profile
    with tab_profile:
        left, right = st.columns(2, gap="large")
        name = resume.get("candidate_name") or "Unknown"
        initials = "".join(w[0] for w in name.split()[:2]).upper() or "?"
        with left:
            body = (f'<div class="who"><div class="avatar">{esc(initials)}</div><div><div class="who-n">{esc(name)}</div>'
                    f'<div class="who-h">{esc(resume.get("headline") or "Headline not identified")}</div></div></div>'
                    '<div class="kv-h">Skills</div>' + chips(resume.get("skills")))
            for field in ["education", "experience", "projects", "achievements"]:
                body += f'<div class="kv-h">{field.title()}</div>' + plain_list(resume.get(field))
            render(panel("Candidate profile", body))
        with right:
            body = (f'<div class="chips" style="margin-bottom:4px"><span class="chip">{esc(job.get("role_title") or "Role not identified")}</span>'
                    f'<span class="chip alt">{esc(job.get("seniority") or "Seniority not identified")}</span></div>'
                    '<div class="kv-h">Required skills</div>' + chips(job.get("required_skills")) +
                    '<div class="kv-h">Preferred skills</div>' + chips(job.get("preferred_skills"), alt=True))
            for field in ["responsibilities", "qualifications"]:
                body += f'<div class="kv-h">{field.title()}</div>' + plain_list(job.get(field))
            body += '<div class="kv-h">Keywords</div>' + chips(job.get("keywords"), alt=True)
            render(panel("Role requirements", body))

    # ---- Prompt engineering
    with tab_prompts:
        section_heading("Behind the results", "Prompt engineering",
                        "The analysis uses a deliberate prompt pipeline rather than a single generic instruction.")
        techniques = [
            ("01", "Role prompting", "The model is assigned recruiter and specialist extraction roles."),
            ("02", "Rubric-based evaluation", "A weighted framework defines how alignment is assessed."),
            ("03", "Few-shot prompting", "An example demonstrates the desired resume bullet transformation."),
            ("04", "Prompt chaining", "Resume extraction → job extraction → candidate comparison."),
            ("05", "Structured output", "Pydantic schemas constrain the response into predictable fields."),
            ("06", "Output format control", "Typed JSON output makes the results usable by the dashboard."),
        ]
        render('<div class="tech">' + "".join(
            f'<div class="tech-c"><div class="tech-n">{n}</div><div class="tech-t">{t}</div><div class="tech-d">{d}</div></div>'
            for n, t, d in techniques) + "</div>")
        with st.expander("View evaluation rubric"):
            st.code(RUBRIC)
        with st.expander("View few-shot example"):
            st.code(FEW_SHOT_EXAMPLE)
        with st.expander("View system prompts"):
            st.code(RESUME_EXTRACTION_SYSTEM + "\n\n" + JOB_EXTRACTION_SYSTEM + "\n\n" + ANALYSIS_SYSTEM)

    # ---- Export
    with st.container(key="export_bar"):
        ex_l, ex_r = st.columns([1.5, .7], vertical_alignment="center")
        with ex_l:
            st.markdown("### Ready for the next step?")
            st.markdown("Download your personalized report and use it to improve your next application.")
        with ex_r:
            st.download_button("↓  Download PDF report", data=build_pdf_report(result),
                               file_name="Resume_Analysis_Report.pdf", mime="application/pdf",
                               use_container_width=True)
    if st.button("Start a new analysis"):
        st.session_state.analysis_result = None
        st.rerun()

render("""
<div class="disclaimer">AI-generated feedback is an informational coaching aid, not an official ATS score or hiring decision.<br>
Resume Analyzer · Thoughtful feedback for your next opportunity</div>
""")
