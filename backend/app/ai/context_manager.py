import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("resume_ai")

INTENT_MAP = {
    "ats": [
        "ats", "ats score", "score", "keyword", "keywords", "density",
        "why is my score", "score low", "increase score", "parse", "meter"
    ],
    "skill_gap": [
        "skill gap", "missing skill", "missing skills", "gap", "gaps",
        "what skills am i missing", "what should i learn next", "what to learn",
        "priority skill", "learn first", "which skills", "skills should i focus",
        "skill to focus", "prioritize skills", "identify skill", "identify gap",
        "my skill gaps", "skill gaps for"
    ],
    "job_role": [
        "job role", "roles", "target role", "suitable", "am i suitable",
        "ready for", "job fit", "matching jobs", "recommend role"
    ],
    "learning": [
        "roadmap", "learning plan", "learning path", "3-month", "curriculum",
        "how long", "study plan", "schedule"
    ],
    "interview": [
        "interview", "mock interview", "questions", "ask me", "quiz",
        "evaluate my answer", "practice interview", "technical question"
    ],
    "resume_improvement": [
        "improve resume", "rewrite", "bullet point", "professional summary",
        "action verb", "resume feedback", "tailor"
    ],
    "resume_analysis": [
        "strongest part", "weakness", "section", "resume", "summary",
        "experience", "projects", "education", "overview"
    ],
    "technical_question": [
        "what is", "explain", "how does", "difference between", "architecture",
        "concept", "how to use", "definition", "rest api", "spring boot",
        "docker", "kubernetes", "microservices"
    ],
}


class ContextManager:
    """
    Intelligent Context Orchestrator:
    1. Detects candidate question intent
    2. Dynamically extracts only relevant candidate profile fields
    3. Truncates and summarizes conversation history
    4. Produces a compact, hallucination-resistant context prompt for Gemini
    """

    def __init__(self, candidate_profile: Optional[Dict[str, Any]] = None):
        self.candidate_profile = candidate_profile or {}

    def detect_intent(self, question: str) -> str:
        q = question.lower().strip()
        for intent, triggers in INTENT_MAP.items():
            for kw in triggers:
                if kw in q:
                    return intent
        return "general_career"

    def select_candidate_context(self, intent: str) -> Dict[str, Any]:
        """Select only relevant attributes based on intent to minimize token bloat."""
        prof = self.candidate_profile or {}
        ctx: Dict[str, Any] = {
            "name": prof.get("name") or "Candidate",
            "target_role": prof.get("target_role") or "Software Engineer",
        }

        if intent in ("ats", "skill_gap", "job_role", "learning", "general_career"):
            ctx["ats_score"] = prof.get("ats_score", 0)
            ctx["skills"] = prof.get("skills", [])
            ctx["missing_skills"] = prof.get("missing_skills", [])
            ctx["matching_skills"] = prof.get("matching_skills", [])
            ctx["has_resume"] = prof.get("has_resume", False)
            ctx["skill_gap_status"] = prof.get("skill_gap_status", "no_resume")

        if intent in ("skill_gap", "learning"):
            ctx["skill_match_percentage"] = prof.get("skill_match_percentage")
            ctx["gap_matrix"] = prof.get("gap_matrix", [])
            ctx["recommendations"] = prof.get("recommendations", [])

        if intent in ("resume_analysis", "resume_improvement"):
            ctx["summary"] = prof.get("summary", "")
            ctx["experience"] = prof.get("experience", [])
            ctx["projects"] = prof.get("projects", [])
            ctx["education"] = prof.get("education", [])
            ctx["skills"] = prof.get("skills", [])
            ctx["ats_score"] = prof.get("ats_score", 0)

        if intent == "interview":
            ctx["target_role"] = prof.get("target_role") or "Software Engineer"
            ctx["skills"] = prof.get("skills", [])
            ctx["projects"] = prof.get("projects", [])
            ctx["missing_skills"] = prof.get("missing_skills", [])

        if intent == "learning":
            ctx["career_roadmap"] = prof.get("career_roadmap", [])

        if intent == "technical_question":
            # For pure technical queries, only mention current target role and related skill
            ctx["skills"] = prof.get("skills", [])[:8]

        return ctx

    def format_compact_context(self, context_data: Dict[str, Any]) -> str:
        """Convert selected context dictionary into a concise markdown text block."""
        if not context_data:
            return "No candidate resume uploaded yet."

        parts = []
        name = context_data.get("name")
        if name:
            parts.append(f"- Candidate Name: {name}")

        role = context_data.get("target_role")
        if role:
            parts.append(f"- Target Role: {role}")

        ats = context_data.get("ats_score")
        if ats is not None:
            parts.append(f"- ATS Compatibility Score: {ats}/100")

        skills = context_data.get("skills")
        if skills:
            skill_list = [str(s) for s in skills[:20]]
            parts.append(f"- Verified Current Skills: {', '.join(skill_list)}")

        matching = context_data.get("matching_skills")
        if matching:
            parts.append(f"- Matching Skills for Target Role: {', '.join([str(s) for s in matching[:15]])}")

        missing = context_data.get("missing_skills")
        if missing:
            parts.append(f"- Missing Skills (Gaps): {', '.join([str(s) for s in missing[:15]])}")

        if context_data.get("skill_gap_status"):
            parts.append(f"- Skill Gap Analysis Status: {context_data['skill_gap_status']}")

        match_percentage = context_data.get("skill_match_percentage")
        if match_percentage is not None:
            parts.append(f"- Skill Match for Target Role: {match_percentage}%")

        gap_matrix = context_data.get("gap_matrix")
        if gap_matrix:
            gap_details = [
                f"{item['skill']} ({item['status']}, {item['priority']} priority)"
                for item in gap_matrix[:15]
            ]
            parts.append(f"- Role Requirement Results: {', '.join(gap_details)}")

        recommendations = context_data.get("recommendations")
        if recommendations:
            recommendation_details = [
                f"{item['skill']}: {item['why']}"
                for item in recommendations[:5]
            ]
            parts.append(f"- Gap Learning Recommendations: {'; '.join(recommendation_details)}")

        projects = context_data.get("projects")
        if projects:
            proj_strs = []
            for p in projects[:3]:
                if isinstance(p, dict):
                    title = p.get("title") or p.get("name", "Project")
                    tech = p.get("technologies") or p.get("tech_stack", "")
                    proj_strs.append(f"{title} ({tech})" if tech else title)
                elif isinstance(p, str):
                    proj_strs.append(p[:60])
            if proj_strs:
                parts.append(f"- Key Resume Projects: {'; '.join(proj_strs)}")

        experience = context_data.get("experience")
        if experience:
            exp_strs = []
            for e in experience[:2]:
                if isinstance(e, dict):
                    title = e.get("title") or e.get("role", "")
                    company = e.get("company", "")
                    exp_strs.append(f"{title} at {company}" if company else title)
                elif isinstance(e, str):
                    exp_strs.append(e[:60])
            if exp_strs:
                parts.append(f"- Experience: {'; '.join(exp_strs)}")

        summary = context_data.get("summary")
        if summary:
            parts.append(f"- Profile Summary: {str(summary)[:250]}")

        return "\n".join(parts) if parts else "Candidate profile loaded."

    @staticmethod
    def trim_and_summarize_history(
        messages: List[Dict[str, str]], max_recent: int = 6
    ) -> str:
        """Keep the last N messages intact and provide a concise summary of earlier messages."""
        if not messages:
            return "No previous conversation history."

        # Normalize message keys ('message' or 'content')
        normalized = []
        for m in messages:
            role = m.get("role") or m.get("sender", "user")
            role_str = "Candidate" if role in ("user", "You") else "Astra"
            text = m.get("message") or m.get("content") or m.get("text", "")
            if text:
                normalized.append(f"{role_str}: {text.strip()}")

        if len(normalized) <= max_recent:
            return "\n".join(normalized)

        older = normalized[:-max_recent]
        recent = normalized[-max_recent:]

        summary_prefix = f"Summary of earlier conversation: Discussed {len(older)} previous exchanges covering candidate background and goals.\n"
        return summary_prefix + "\n".join(recent)

    def build_context_package(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Construct full context package for prompt synthesis."""
        intent = self.detect_intent(user_message)
        selected_data = self.select_candidate_context(intent)
        compact_text = self.format_compact_context(selected_data)
        history_text = self.trim_and_summarize_history(conversation_history or [])

        return {
            "intent": intent,
            "candidate_data": selected_data,
            "compact_context": compact_text,
            "history": history_text,
        }


def build_context_for_gemini(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    candidate_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    manager = ContextManager(candidate_profile or {})
    return manager.build_context_package(user_message, conversation_history)
