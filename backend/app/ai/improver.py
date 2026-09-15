from typing import Dict, Any, List
import re

def enhance_single_bullet(text: str, target_role: str = "Software Engineer") -> str:
    """Rewrite a single resume bullet point into an action-verb driven, metric-quantified accomplishment statement."""
    if not text or not text.strip():
        return "Engineered high-performance application modules, reducing execution latency by 35%."

    clean = text.strip()
    lowered = clean.lower()

    action_verbs = ["Architected", "Engineered", "Optimized", "Spearheaded", "Implemented", "Automated", "Streamlined", "Deployed"]
    verb = action_verbs[hash(clean) % len(action_verbs)]

    if "worked on" in lowered or "built" in lowered or "made" in lowered or "created" in lowered or "developed" in lowered:
        cleaned_text = re.sub(r'^(worked on|built|made|created|developed|did)\s+', '', clean, flags=re.IGNORECASE)
        return f"{verb} {cleaned_text}, improving operational efficiency and reducing system latency by 30%."

    if not any(v.lower() in lowered for v in action_verbs):
        return f"{verb} {clean}, ensuring high reliability, scalability, and 99.9% uptime."

    if not re.search(r'\d+%', clean) and not re.search(r'\d+', clean):
        return f"{clean}, accelerating delivery cycles by 25%."

    return clean

def generate_resume_improvements(parsed_data: Dict[str, Any], target_role: str = "Software Engineer") -> Dict[str, Any]:
    sections = parsed_data.get("sections", {})
    all_skills = parsed_data.get("all_skills", [])
    personal_info = parsed_data.get("personal_info", {})
    current_summary = sections.get("summary", "")

    # 1. Summary Rewrites
    name = personal_info.get("name", "Software Professional")
    skills_str = ", ".join(all_skills[:4]) if all_skills else "software engineering, modern frameworks, and system design"
    
    suggested_summary_before = current_summary if current_summary else "Experienced software developer skilled in programming and building applications."
    suggested_summary_after = (
        f"Results-driven {target_role} with proven expertise in {skills_str}. "
        f"Adept at engineering scalable backend architectures, optimizing API performance, "
        f"and collaborating in Agile team environments to deliver high-quality software solutions."
    )

    # 2. Experience Bullet Point Rewrites
    experience_rewrites = [
        {
            "original_text": "Worked on a website using JavaScript.",
            "improved_text": "Developed a responsive, modern web application using JavaScript (ES6+), improving user interaction and reducing page load time by 28%.",
            "type": "Rewrite Existing"
        },
        {
            "original_text": "Built backend APIs for user management.",
            "improved_text": "Engineered high-throughput RESTful APIs with FastAPI/Node.js, handling 10,000+ daily active user authentication requests with zero downtime.",
            "type": "Rewrite Existing"
        },
        {
            "original_text": "Fixed bugs and database issues.",
            "improved_text": "Optimized database queries and resolved critical production bugs, reducing database query latency by 40%.",
            "type": "Rewrite Existing"
        }
    ]

    # 3. Project Impact Enhancements
    project_improvements = [
        {
            "original_text": "Made a resume scanner application.",
            "improved_text": "Architected an AI-powered Resume Analyzer using Python, spaCy, and FastAPI, automated skill extraction across 500+ documents with 92% extraction accuracy.",
            "type": "Rewrite Existing"
        },
        {
            "original_text": "Created frontend dashboard.",
            "improved_text": "Designed an interactive analytics dashboard utilizing React, Vite, and Recharts, delivering real-time metric visualizations for candidate evaluation.",
            "type": "Rewrite Existing"
        }
    ]

    # 4. Recommended Skill Additions
    recommended_skill_additions = [
        "Docker (Containerization)",
        "GitHub Actions (CI/CD Automation)",
        "PostgreSQL / Redis (Caching & Relational Data)",
        "Unit Testing (PyTest / Jest)"
    ]

    # 5. Formatting & Layout Audit
    formatting_audit = [
        "Ensure standard fonts (Inter, Roboto, Arial) are used rather than custom non-standard typefaces.",
        "Avoid multi-column tables or header/footer graphic elements that obscure ATS document parsing.",
        "Maintain clean section headings (e.g. 'Professional Experience', 'Education', 'Technical Skills').",
        "Export and submit in clear text PDF or DOCX format for optimal ATS parsing fidelity."
    ]

    return {
        "summary_improvement": {
            "before": suggested_summary_before,
            "after": suggested_summary_after,
            "notes": "Enhanced with targeted role keywords and proactive impact phrasing."
        },
        "experience_bullet_improvements": experience_rewrites,
        "project_improvements": project_improvements,
        "recommended_skill_additions": recommended_skill_additions,
        "formatting_audit": formatting_audit
    }
