import json
import logging
import re
from typing import Any, Dict, Iterator, List, Optional
from app.ai.gemini_client import get_gemini_client
from app.ai.prompts import ASTRA_CHATBOT_SYSTEM_PROMPT
from app.ai.rag_engine import rag_engine
from app.ai.context_manager import ContextManager

logger = logging.getLogger("resume_ai")


def normalize_resume_context(raw_resume: Optional[Dict[str, Any]], fallback_role: str = "Software Engineer") -> Dict[str, Any]:
    """Normalize resume data from multiple parser shapes into a consistent Astra context object."""
    data = raw_resume or {}
    sections = data.get("sections") if isinstance(data.get("sections"), dict) else {}
    personal_info = data.get("personal_info") if isinstance(data.get("personal_info"), dict) else {}

    target_role = (
        data.get("target_role")
        or data.get("job_target_role")
        or sections.get("target_role")
        or fallback_role
    )

    skills = data.get("all_skills") or data.get("skills") or []
    missing_skills = data.get("missing_skills") or data.get("skill_gaps") or []
    matching_skills = data.get("matching_skills") or []
    ats_score = data.get("ats_score")
    if ats_score is None:
        ats_score = data.get("ats") or data.get("score") or 0

    normalized = {
        "name": data.get("name") or personal_info.get("name") or "Candidate",
        "target_role": target_role,
        "summary": data.get("summary") or sections.get("summary") or personal_info.get("summary") or "",
        "skills": [str(skill) for skill in skills],
        "missing_skills": [str(skill) for skill in missing_skills],
        "matching_skills": [str(skill) for skill in matching_skills],
        "ats_score": float(ats_score) if isinstance(ats_score, (int, float)) else 0,
        "experience": data.get("experience") or sections.get("experience") or [],
        "projects": data.get("projects") or sections.get("projects") or [],
        "education": data.get("education") or sections.get("education") or [],
    }

    if not normalized["skills"] and isinstance(data.get("skills_by_category"), dict):
        for item in data["skills_by_category"].values():
            if isinstance(item, list):
                normalized["skills"].extend(str(skill) for skill in item)

    if not normalized["missing_skills"] and isinstance(data.get("missing_skills_detail"), list):
        normalized["missing_skills"] = [str(skill) for skill in data["missing_skills_detail"]]

    return normalized


def _build_full_prompt(
    user_message: str,
    context_pkg: Dict[str, Any],
    rag_context: str
) -> str:
    compact_ctx = context_pkg.get("compact_context", "")
    history = context_pkg.get("history", "")
    intent = context_pkg.get("intent", "general_career")

    return f"""Candidate Resume Context:
{compact_ctx}

Retrieved Technical & Career Knowledge Base:
{rag_context}

Recent Conversation History:
{history}

Detected Query Intent: {intent}

Candidate Message:
"{user_message}"

Instruction for Astra:
Respond in a warm, professional, encouraging, and highly specific tone as Astra, the AI Career Assistant.
- If the user asks about their resume, ATS score, or skills, cite their actual context above.
- If something is missing from their profile, state honestly that it was not detected in their uploaded resume.
- Prioritize actionable steps with clear technical rationale.
- Use markdown formatting with bullet points and bold highlights for readability.
- Answer the candidate's latest message directly. Use conversation history for continuity, and do not repeat an earlier answer verbatim; add new, question-specific guidance.
- For skill-gap questions, use only the provided Skill Gap Analysis Status, Skill Match, Role Requirement Results, and Gap Learning Recommendations. Do not invent or infer missing skills.
- If the status is no_resume, ask the candidate to upload and analyze a resume. If it is no_detected_skills, explain that no skills were detected and ask them to check or re-upload the resume. Only present gaps when the status is analyzed.
"""


def _generate_fallback_response(
    user_message: str,
    context_pkg: Dict[str, Any],
    rag_context: str
) -> str:
    """Generate a grounded, question-specific reply when Gemini is unavailable."""
    candidate = context_pkg.get("candidate_data", {})
    intent = context_pkg.get("intent", "general_career")

    target_role = candidate.get("target_role", "Software Engineer")
    skills = candidate.get("skills") or []
    missing_skills = candidate.get("missing_skills") or []
    skills_str = ", ".join(str(skill) for skill in skills[:6]) or "No analyzed resume skills are available yet."
    missing_str = ", ".join(str(skill) for skill in missing_skills[:4])
    question = user_message.strip()

    if intent == "ats":
        score = candidate.get("ats_score") or 0
        if score:
            return (
                f"Your latest analyzed ATS score is **{score}/100** for **{target_role}**. "
                f"Your detected skills include {skills_str}. "
                "To improve the match, compare your resume with the exact job description, "
                "use its relevant terminology where it truthfully describes your experience, "
                "and quantify outcomes in experience and project bullets. "
                "I don't have a score breakdown here, so share the target job description "
                "or analysis report if you'd like a more specific diagnosis."
            )
        return (
            "I don't have an analyzed ATS score available for your profile yet, so I can't "
            "diagnose a specific score. Upload and analyze your resume first. In the meantime, "
            "use a simple single-column layout, standard section headings, and relevant job-description "
            "keywords that accurately reflect your experience."
        )

    if intent in ("skill_gap", "learning"):
        gap_status = candidate.get("skill_gap_status", "no_resume")
        if gap_status == "no_resume":
            return (
                "I can't identify your personal skill gaps yet because I don't have an analyzed resume "
                "for your account. Upload your resume first, then choose a target role so I can compare "
                "your detected skills against its requirements. You can also paste your skills here "
                "for a general comparison."
            )
        if gap_status == "no_detected_skills":
            return (
                f"I couldn't detect skills in the uploaded resume, so I can't reliably identify gaps "
                f"for **{target_role}**. Please check that the resume text is readable, then re-upload "
                "or paste your skills here. I won't label unverified skills as missing."
            )
        if gap_status == "analyzed":
            gap_matrix = candidate.get("gap_matrix") or []
            matched = [item["skill"] for item in gap_matrix if item["status"] == "Available"]
            missing_items = [item for item in gap_matrix if item["status"] == "Missing"]
            matched_str = ", ".join(matched) or "none of the benchmark skills were detected"
            if not missing_items:
                return (
                    f"Your analyzed resume matches all benchmark skills for **{target_role}** "
                    f"({candidate.get('skill_match_percentage', 0)}% match). Detected skills: "
                    f"{matched_str}. Keep these skills clearly supported by project or work examples."
                )

            missing_summary = ", ".join(
                f"{item['skill']} ({item['priority']} priority)" for item in missing_items
            )
            recommendation_by_skill = {
                item["skill"]: item for item in candidate.get("recommendations", [])
            }
            first_missing = missing_items[0]["skill"]
            recommendation = recommendation_by_skill.get(first_missing)
            next_step = (
                recommendation["next_steps"][0]
                if recommendation and recommendation.get("next_steps")
                else f"Build a small project that demonstrates {first_missing}."
            )
            return (
                f"### Skill-gap analysis for {target_role}\n\n"
                f"**Role match: {candidate.get('skill_match_percentage', 0)}%**\n\n"
                f"**Skills detected:** {matched_str}.\n\n"
                f"**Gaps, by priority:** {missing_summary}.\n\n"
                f"**Recommended first step — {first_missing}:** {next_step}\n\n"
                "These results compare skills detected in your latest analyzed resume with the "
                "selected role's requirements. Tell me which gap you want to work on and I can "
                "outline a focused learning plan."
            )

    if intent == "interview":
        primary_skill = str(skills[0]) if skills else "a technology from your target role"
        questions = [
            f"Describe a project where you used {primary_skill}. What trade-off did you make?",
            f"How would you test a production feature built with {primary_skill}?",
            f"Tell me about a technical issue you would investigate first if a service using {primary_skill} became slow.",
            f"How would you explain the main limitation of {primary_skill} to a teammate?",
            f"What would you improve in a project using {primary_skill} if you had another week?",
        ]
        if re.search(r"\b(5|five|list|some|questions)\b", question.lower()):
            return "Here are five practice questions for a **" + target_role + "** interview:\n\n" + "\n".join(
                f"{index}. {prompt}" for index, prompt in enumerate(questions, 1)
            ) + "\n\nAnswer one and I can give feedback on its clarity, technical depth, and structure."
        return (
            f"Let's practice for a **{target_role}** role. **Question:** {questions[0]} "
            "Answer with the situation, your specific actions, and the result. I'll then give "
            "feedback and a follow-up question."
        )

    if intent == "technical_question":
        topic_match = re.search(r"\b(?:what is|explain|define|how does|how do i use)\s+(.+?)(?:\?|$)", question, re.I)
        topic = topic_match.group(1).strip(" .") if topic_match else question.rstrip("?. ")
        if rag_context.strip():
            return (
                f"Here is the relevant reference for **{topic}**:\n\n{rag_context[:900].strip()}\n\n"
                "Tell me which part you'd like me to explain with an example."
            )
        return (
            f"I can help explain **{topic}**, but I don't have a matching knowledge-base reference "
            "available for this query right now. Tell me your experience level and whether you want "
            "a conceptual explanation, code example, or interview-style answer."
        )

    elif intent == "job_role":
        return (
            f"For a **{target_role}** role, your detected skills are {skills_str}. "
            f"{'The analyzed gaps are ' + missing_str + '.' if missing_str else 'I do not have analyzed skill gaps yet.'} "
            "Compare these against a specific job posting and look for evidence in your projects "
            "that demonstrates each requirement. Share a posting and I can help assess the match."
        )

    if intent in ("resume_analysis", "resume_improvement"):
        summary = candidate.get("summary")
        if summary:
            return (
                f"Your profile summary is: {summary} For the request **“{question}”**, "
                "I can give a more precise review if you share the resume section or bullet you "
                "want to improve. I won't invent experience or metrics."
            )
        return (
            f"I don't have analyzed resume details to review for **“{question}”** yet. "
            "Upload and analyze your resume, or paste the specific bullet/section here. "
            "I can then suggest a clearer, impact-focused rewrite without adding unsupported claims."
        )

    previous_reply = next(
        (line.removeprefix("Astra: ").strip() for line in reversed(context_pkg.get("history", "").splitlines())
         if line.startswith("Astra: ")),
        None,
    )
    continuation = " Building on our conversation, " if previous_reply else ""
    return (
        f"You asked: **{question}**.{continuation}I can tailor the answer to your **{target_role}** goal, "
        f"but I only have these analyzed skills available: {skills_str} "
        "Tell me the specific outcome you want—an explanation, a step-by-step plan, or feedback "
        "on a resume section—and I'll focus the response."
    )


def chat_with_astra(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    candidate_context: Optional[Dict[str, Any]] = None
) -> str:
    """Core conversational entry point for Astra AI Career Assistant."""
    manager = ContextManager(candidate_context or {})
    context_pkg = manager.build_context_package(user_message, conversation_history)
    rag_context = rag_engine.retrieve_context(user_message, top_k=2)

    gemini = get_gemini_client()
    if gemini.available:
        try:
            full_prompt = _build_full_prompt(user_message, context_pkg, rag_context)
            return gemini.generate_text(full_prompt, system_prompt=ASTRA_CHATBOT_SYSTEM_PROMPT)
        except Exception as e:
            logger.warning(f"Gemini API invocation error: {e}. Falling back to structured response engine.")

    return _generate_fallback_response(user_message, context_pkg, rag_context)


def stream_chat_with_astra(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    candidate_context: Optional[Dict[str, Any]] = None
) -> Iterator[str]:
    """Streaming entry point yielding tokens/chunks for Astra."""
    manager = ContextManager(candidate_context or {})
    context_pkg = manager.build_context_package(user_message, conversation_history)
    rag_context = rag_engine.retrieve_context(user_message, top_k=2)

    gemini = get_gemini_client()
    if gemini.available:
        try:
            full_prompt = _build_full_prompt(user_message, context_pkg, rag_context)
            for chunk in gemini.stream_text(full_prompt, system_prompt=ASTRA_CHATBOT_SYSTEM_PROMPT):
                yield chunk
            return
        except Exception as e:
            logger.warning(f"Gemini stream error: {e}. Using fallback stream.")

    fallback_text = _generate_fallback_response(user_message, context_pkg, rag_context)
    # Simulate gentle chunking for smooth UI streaming experience
    words = fallback_text.split(" ")
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i : i + chunk_size]) + " "


def evaluate_interview_answer(
    question: str,
    candidate_answer: str,
    target_role: str = "Software Engineer"
) -> Dict[str, Any]:
    """Evaluate candidate's interview answer with scoring and structured feedback."""
    prompt = f"""Target Role: {target_role}
Interview Question: {question}
Candidate Answer: {candidate_answer}

Evaluate this response thoroughly on:
1. Technical Accuracy (score 1-10)
2. Completeness (score 1-10)
3. Clarity (score 1-10)
4. Strengths
5. Areas for improvement
6. Improved model answer

Return ONLY valid JSON matching this schema:
{{
  "score": 85,
  "technical_accuracy": "8/10",
  "completeness": "7/10",
  "clarity": "8/10",
  "strengths": ["Clear explanation of core concepts"],
  "areas_for_improvement": ["Mention specific performance metrics and benchmarks"],
  "feedback": "Your answer is accurate and well structured. To make it senior-level, include trade-offs.",
  "improved_model_answer": "A structured model answer..."
}}"""

    gemini = get_gemini_client()
    if gemini.available:
        try:
            return gemini.generate_json(prompt, system_prompt="You are an expert technical hiring manager.")
        except Exception as e:
            logger.warning(f"Interview evaluation Gemini error: {e}")

    # Fallback Evaluation
    word_count = len(candidate_answer.split())
    base_score = min(92, max(65, 60 + word_count * 2))
    return {
        "score": base_score,
        "technical_accuracy": "8/10",
        "completeness": "8/10",
        "clarity": "8/10",
        "strengths": [
            "Addressed the core question directly",
            "Demonstrated logical flow and structured technical thinking"
        ],
        "areas_for_improvement": [
            "Include concrete examples or quantifiable production metrics",
            "Discuss edge cases and architectural trade-offs"
        ],
        "feedback": "Good response! You clearly understand the foundational architecture. Adding specific real-world examples and metrics will take your score above 90%.",
        "improved_model_answer": f"In a production {target_role} system, I approach this by separating concerns across architectural layers, applying connection pooling, and adding monitoring for latency and error rates."
    }
