"""Sample analysis result so the dashboard can be previewed without an API key."""


def get_demo_result() -> dict:
    return {
        "model": "demo-data",
        "resume_profile": {
            "candidate_name": "Aarav Sharma",
            "headline": "Computer Science undergraduate with Python and full-stack project experience",
            "skills": ["Python", "Java", "C++", "SQL", "Git", "Flask", "React", "HTML/CSS"],
            "education": ["B.Tech Computer Science, Bennett University (2022 - 2026), CGPA 8.6"],
            "experience": [
                "Software Engineering Intern, TechNova - built REST endpoints and wrote unit tests",
                "Teaching Assistant, Data Structures - mentored 40 students",
            ],
            "projects": [
                "Campus Event Portal - Flask + SQL web app used by 300+ students",
                "Sorting Visualizer - interactive React app for algorithm learning",
            ],
            "achievements": ["Top 10 finalist, Smart India Hackathon", "500+ problems solved on LeetCode"],
            "evidence_notes": [],
        },
        "job_profile": {
            "role_title": "Software Development Engineer Intern",
            "seniority": "Internship / Entry level",
            "required_skills": ["Python / Java / C++", "Data structures & algorithms", "OOP", "Git"],
            "preferred_skills": ["REST APIs", "SQL", "Cloud platforms", "Testing", "System design"],
            "responsibilities": [
                "Build, test and maintain software components",
                "Participate in code reviews",
                "Debug issues and improve reliability",
            ],
            "qualifications": ["Pursuing a degree in Computer Science or related field"],
            "keywords": ["APIs", "testing", "debugging", "collaboration", "algorithms"],
        },
        "analysis": {
            "match_score": 78,
            "match_summary": (
                "Aarav is a strong fit for this internship. The resume shows solid programming "
                "fundamentals, relevant project work and hands-on API and testing experience. "
                "The main gaps are cloud exposure and explicit system design evidence."
            ),
            "strengths": [
                "Proficient in Python, Java and C++, matching the core language requirement.",
                "Internship experience building REST endpoints with unit tests.",
                "Two substantial projects with real users demonstrate practical delivery.",
                "Hackathon finalist placement signals collaboration under pressure.",
            ],
            "improvement_areas": [
                "No cloud platform experience (AWS, GCP or Azure) is visible.",
                "System design knowledge is not demonstrated in any project.",
                "Several bullets describe tasks rather than measurable outcomes.",
            ],
            "skill_assessments": [
                {"skill": "Python", "status": "Strong evidence", "importance": "High",
                 "evidence": "Used in the Campus Event Portal and the TechNova internship."},
                {"skill": "Data structures & algorithms", "status": "Strong evidence", "importance": "High",
                 "evidence": "Teaching assistant for DSA; 500+ LeetCode problems; Sorting Visualizer."},
                {"skill": "Git", "status": "Strong evidence", "importance": "High",
                 "evidence": "Listed in skills and implied by team internship work."},
                {"skill": "REST APIs", "status": "Strong evidence", "importance": "Medium",
                 "evidence": "Built REST endpoints during the TechNova internship."},
                {"skill": "SQL", "status": "Partial evidence", "importance": "Medium",
                 "evidence": "Listed as a skill and used in the Campus Event Portal, no detail given."},
                {"skill": "Testing", "status": "Partial evidence", "importance": "Medium",
                 "evidence": "Unit tests mentioned once in the internship bullet."},
                {"skill": "Cloud platforms", "status": "Not found", "importance": "Medium",
                 "evidence": "No cloud service or deployment target appears in the resume."},
                {"skill": "System design", "status": "Not found", "importance": "Low",
                 "evidence": "No architecture or scalability discussion found."},
            ],
            "category_scores": [
                {"category": "Technical skills", "score": 84, "weight_percent": 30,
                 "rationale": "Covers all required languages and most preferred tools."},
                {"category": "Projects & practical work", "score": 80, "weight_percent": 25,
                 "rationale": "Two real-world projects with users."},
                {"category": "Relevant experience", "score": 72, "weight_percent": 20,
                 "rationale": "One relevant internship; impact not quantified."},
                {"category": "Education", "score": 90, "weight_percent": 10,
                 "rationale": "Currently pursuing a CS degree with a strong CGPA."},
                {"category": "Role alignment", "score": 62, "weight_percent": 15,
                 "rationale": "Missing cloud and system design signals."},
            ],
            "rewritten_bullets": [
                {
                    "original": "Worked on REST endpoints for the backend team.",
                    "improved": "Built and tested REST API endpoints for the backend team, adding unit tests that covered the new routes.",
                    "rationale": "Uses a strong action verb and surfaces the testing evidence the role asks for.",
                    "evidence_warning": "Add a metric (e.g. number of endpoints) only if you can verify it.",
                },
                {
                    "original": "Made a web app for campus events.",
                    "improved": "Developed a Flask and SQL web application for campus events, used by 300+ students.",
                    "rationale": "Names the stack and the real-world usage already stated on the resume.",
                    "evidence_warning": "",
                },
            ],
            "recommended_actions": [
                "Deploy one project to a free cloud tier and add the link to your resume.",
                "Add one measurable outcome to every internship bullet.",
                "Write a short design note for the Campus Event Portal covering scaling and the database schema.",
                "Mirror the job description keywords (APIs, testing, debugging) where they are truthful.",
            ],
            "interview_preparation": [
                "Walk through the data model and queries of the Campus Event Portal.",
                "Explain time and space complexity for your most-used algorithms.",
                "Prepare a story about debugging a production-style issue during your internship.",
                "Be ready to discuss how you would deploy and scale a small web service.",
            ],
            "fairness_note": "This estimate considers only the resume text provided and not protected characteristics.",
        },
    }
