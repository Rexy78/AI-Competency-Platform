import json
import logging
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("resume_ai")

try:
    from langgraph.graph import StateGraph
    LANGGRAPH_AVAILABLE = True
except Exception:
    LANGGRAPH_AVAILABLE = False

from app.ai.gemini_client import get_gemini_client


def _normalize_skill_list(skills: Optional[List[str]]) -> List[str]:
    if not skills:
        return []
    result = []
    for skill in skills:
        value = str(skill).strip()
        if value:
            result.append(value)
    return result


def _extract_profile_from_resume(user, db):
    from app.models.models import Resume, ResumeAnalysis

    resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user.id).order_by(ResumeAnalysis.created_at.desc()).first()

    profile = {
        "name": getattr(user, "full_name", "Candidate"),
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "certifications": [],
        "ats_score": 75,
        "target_role": "Software Engineer",
        "matching_skills": [],
        "missing_skills": [],
        "career_roadmap": [],
    }

    if resume and isinstance(resume.parsed_json, dict):
        raw = resume.parsed_json
        profile["skills"] = _normalize_skill_list(raw.get("all_skills") or raw.get("skills") or [])
        profile["education"] = raw.get("education") or []
        profile["experience"] = raw.get("experience") or []
        profile["projects"] = raw.get("projects") or []
        profile["certifications"] = raw.get("certifications") or []
        profile["target_role"] = raw.get("target_role") or raw.get("job_target_role") or profile["target_role"]

    if analysis:
        profile["ats_score"] = float(analysis.ats_score or 75)
        profile["target_role"] = analysis.target_role or profile["target_role"]

    if not profile["skills"]:
        profile["skills"] = ["Java", "SQL", "Python", "REST API", "Docker"]

    return profile


def _extract_missing_skills(profile: Dict[str, Any], target_role: str) -> List[str]:
    known = {skill.lower() for skill in profile.get("skills", [])}
    role_map = {
        "java developer": ["spring boot", "hibernate", "rest api", "docker", "microservices", "mysql"],
        "backend developer": ["spring boot", "rest api", "sql", "docker", "redis", "microservices"],
        "full stack developer": ["react", "node.js", "rest api", "sql", "docker"],
        "data scientist": ["python", "pandas", "machine learning", "sql", "model evaluation"],
    }
    required = role_map.get(target_role.lower(), ["rest api", "sql", "docker", "system design"])
    missing = [item for item in required if item.lower() not in known]
    return missing[:6]


def _job_description_keywords(job_description: Optional[str]) -> List[str]:
    if not job_description:
        return []
    text = job_description.lower()
    keywords = [
        "java", "spring boot", "sql", "mysql", "rest api", "docker", "aws",
        "microservices", "kafka", "hibernate", "redis", "system design",
        "react", "node", "python", "ml"
    ]
    return [keyword for keyword in keywords if keyword in text]


def _default_interview_plan(profile, target_role, interview_type, difficulty, total_questions):
    missing = profile.get("missing_skills") or _extract_missing_skills(profile, target_role)
    interview_type = (interview_type or "").lower()
    primary = [
        ("Java", 25),
        ("Spring Boot", 20),
        ("SQL", 15),
        ("REST API", 15),
        ("Project Experience", 15),
        ("Behavioral / HR", 10),
    ]
    if interview_type == "technical":
        primary = [("Java", 28), ("Spring Boot", 24), ("REST API", 18), ("SQL", 15), ("System Design", 15)]
    elif interview_type == "hr":
        primary = [("Behavioral / HR", 40), ("Project Experience", 30), ("Communication", 30)]
    elif interview_type == "resume-based":
        primary = [("Project Experience", 30), ("Java", 25), ("SQL", 20), ("REST API", 15), ("Behavioral / HR", 10)]
    elif interview_type == "coding":
        primary = [("Coding", 35), ("Project Experience", 25), ("Java", 20), ("System Design", 20)]
    elif interview_type == "communication":
        primary = [("Communication", 45), ("Behavioral / HR", 30), ("Project Experience", 25)]
    elif interview_type == "aptitude":
        primary = [("Aptitude", 50), ("Problem Solving", 30), ("Logical Reasoning", 20)]
    elif interview_type == "quick-test":
        primary = [("Technical", 40), ("Aptitude", 30), ("Communication", 30)]

    categories = [{"name": name, "percentage": pct} for name, pct in primary]
    if missing and interview_type not in {"aptitude", "coding", "communication"}:
        categories[0] = {"name": missing[0].title(), "percentage": max(20, categories[0]["percentage"])}
    return {"target_role": target_role, "difficulty": difficulty, "total_questions": total_questions, "categories": categories}


def plan_interview(profile: Dict[str, Any], target_role: str, interview_type: str, difficulty: str, total_questions: int, job_description: Optional[str]=None) -> Dict[str, Any]:
    gemini = get_gemini_client()
    prompt = f"""
    Analyze this candidate profile and create an adaptive interview plan as JSON.
    Candidate profile: {json.dumps(profile, ensure_ascii=False, indent=2)}
    Target role: {target_role}
    Interview type: {interview_type}
    Difficulty: {difficulty}
    Total questions: {total_questions}
    Job description keywords: {', '.join(_job_description_keywords(job_description)) or 'None'}
    Return JSON only with keys: target_role, difficulty, total_questions, categories (array of objects with keys name and percentage).
    """
    try:
        if gemini and getattr(gemini, "available", False):
            result = gemini.generate_json(prompt)
            if isinstance(result, dict) and result.get("categories"):
                return result
    except Exception as exc:
        logger.warning("Gemini interview planning failed: %s", exc)
    return _default_interview_plan(profile, target_role, interview_type, difficulty, total_questions)


def _category_templates(skill_name: str, target_role: str) -> List[str]:
    templates = {
        "java": [
            "Explain the difference between Java and JavaScript in the context of backend development.",
            "What is the JVM and why is it important in Java applications?",
            "Explain how Java garbage collection affects application performance."
        ],
        "spring boot": [
            "Explain the difference between Spring Framework and Spring Boot.",
            "What problem does dependency injection solve in Spring Boot?",
            "Explain how a Spring Boot REST controller works."
        ],
        "sql": [
            "How would you optimize a slow SQL query?",
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "How do indexes improve database performance?"
        ],
        "rest api": [
            "Explain the difference between PUT and PATCH in REST APIs.",
            "How do you handle authentication in a REST API?",
            "What are HTTP status codes and why do they matter?"
        ],
        "docker": [
            "What is the advantage of containerizing an application?",
            "How is Docker different from a virtual machine?",
            "Why do teams use Docker Compose in backend projects?"
        ],
        "project experience": [
            "Explain the architecture of a project you built and the problems it solved.",
            "What trade-offs did you consider in your most significant project?",
            "Describe a challenge you solved during implementation and how you measured success."
        ],
        "behavioral": [
            "Tell me about a time you handled a difficult deadline or team issue.",
            "Describe a situation where you improved a process in your project.",
            "How do you prioritize competing tasks when working on multiple deliverables?"
        ],
    }
    key = skill_name.lower().replace("/", " ")
    for known_key in templates:
        if known_key in key:
            return templates[known_key]
    return [
        f"Explain how you have used {skill_name} in a real project and why it mattered.",
        f"What are the main trade-offs when working with {skill_name}?",
        f"How would you teach a beginner to understand {skill_name}?"
    ]


def _topic_from_question(question: str) -> str:
    lower = question.lower()
    for keyword in ["spring boot", "java", "sql", "docker", "rest", "project", "behavioral", "hr", "design", "aptitude", "coding", "communication"]:
        if keyword in lower:
            return keyword.title()
    return "General"


def generate_question_for_session(state: Dict[str, Any]) -> Dict[str, Any]:
    profile = state.get("candidate_profile") or {}
    target_role = state.get("target_role") or "Software Engineer"
    interview_type = (state.get("interview_type") or "").lower()
    skill_gaps = profile.get("missing_skills") or []
    skills = profile.get("skills") or []
    recent_history = state.get("question_history") or []
    previous_scores = [item.get("score", 0) for item in recent_history if isinstance(item, dict)]
    recent_avg = sum(previous_scores) / len(previous_scores) if previous_scores else 0
    coding_language = (state.get("coding_language") or "Java").lower()

    aptitude_bank = [
        {"question": "If 5 workers complete a task in 12 days, how many days will 3 workers take at the same rate?", "options": ["18 days", "20 days", "24 days", "30 days"], "correct_option": "B", "explanation": "Work = 5 × 12 = 60 worker-days. For 3 workers, time = 60 / 3 = 20 days."},
        {"question": "A sequence is 2, 6, 18, 54, ... What is the 5th term?", "options": ["72", "108", "162", "216"], "correct_option": "C", "explanation": "Each term is multiplied by 3; 54 × 3 = 162."},
        {"question": "The median of [2, 3, 7, 10, 15] is:", "options": ["3", "7", "10", "15"], "correct_option": "B", "explanation": "The middle value in the sorted list is 7."},
        {"question": "If P(A) = 0.4 and P(B) = 0.3 and A and B are independent, what is P(A and B)?", "options": ["0.10", "0.12", "0.30", "0.70"], "correct_option": "B", "explanation": "Independent events multiply: 0.4 × 0.3 = 0.12."},
        {"question": "A train moving at 60 km/h takes 2 hours less than a train moving at 40 km/h for the same distance. The distance is:", "options": ["100 km", "120 km", "180 km", "240 km"], "correct_option": "D", "explanation": "Difference equation gives d = 240 km."},
        {"question": "If a person saves 20% of salary and spends the rest, what percentage is spent?", "options": ["20%", "40%", "60%", "80%"], "correct_option": "D", "explanation": "If 20% is saved, 80% is spent."},
        {"question": "What is the average of 12, 18, 24, and 30?", "options": ["18", "20", "21", "24"], "correct_option": "B", "explanation": "Total = 84; average = 84 / 4 = 21."},
        {"question": "If 3 notebooks cost Rs. 120, what is the cost of 5 notebooks?", "options": ["180", "200", "220", "240"], "correct_option": "B", "explanation": "Each notebook costs 40; 5 notebooks cost 200."},
        {"question": "A rectangle has length 10 and breadth 6. What is its area?", "options": ["16", "30", "60", "100"], "correct_option": "C", "explanation": "Area = length × breadth = 10 × 6 = 60."},
        {"question": "If 15% of a number is 45, what is the number?", "options": ["225", "300", "450", "600"], "correct_option": "B", "explanation": "0.15 × x = 45 => x = 300."},
    ]

    communication_bank = [
        {"question": "What is the best way to respond when a teammate misses a deadline?", "options": ["Blame them publicly", "Discuss root cause and support planning", "Ignore the issue", "Change the project scope without discussion"], "correct_option": "B", "explanation": "Professional communication focuses on root cause, support, and a corrective plan."},
        {"question": "Which behavior best shows strong communication in a technical team?", "options": ["Speaking only to senior managers", "Explaining issues clearly with evidence and next steps", "Avoiding updates until the end", "Using jargon without context"], "correct_option": "B", "explanation": "Clear communication with context and action steps is effective for collaboration."},
        {"question": "How should you handle disagreement with a stakeholder?", "options": ["Argue aggressively", "Listen, acknowledge concerns, and align on evidence", "Stop responding", "Accept all demands without analysis"], "correct_option": "B", "explanation": "Constructive disagreement needs listening and evidence-based alignment."},
        {"question": "What is the best way to explain a technical issue to a non-technical manager?", "options": ["Use heavy jargon", "Give a business impact and plain-language explanation", "Send code only", "Avoid explanation"], "correct_option": "B", "explanation": "Translate technical issues into business impact and simple language."},
        {"question": "Which of these is a strong example of feedback?", "options": ["You are bad at this task", "Your report lacked clarity; here is a template that will help", "I do not care", "You should already know this"], "correct_option": "B", "explanation": "Specific, actionable, respectful feedback improves performance."},
        {"question": "How should you communicate project risk to a manager?", "options": ["Hide it until deadline", "Share the issue, impact, and mitigation plan", "Only mention it in group chat", "Let the team handle it quietly"], "correct_option": "B", "explanation": "Transparent communication with mitigation is professional and trusted."},
        {"question": "Which response illustrates active listening?", "options": ["Interrupt immediately", "Summarize the concern before responding", "Ignore the concern", "Change the topic"], "correct_option": "B", "explanation": "Active listening means confirming understanding before replying."},
        {"question": "What is the best way to write a project update?", "options": ["Only mention personal tasks", "Include status, blockers, and next steps", "Skip dates and milestones", "Write a long history lesson"], "correct_option": "B", "explanation": "Effective updates are brief, clear, and actionable."},
        {"question": "During conflict, which response is most professional?", "options": ["Attack the other person", "Stay calm and focus on facts", "Blame the team", "Refuse to talk"], "correct_option": "B", "explanation": "Professional conflict resolution stays calm and fact-based."},
        {"question": "What makes a good technical presentation?", "options": ["Too much jargon", "Clear structure, examples, and business relevance", "No preparation", "Only code snippets"], "correct_option": "B", "explanation": "A good presentation is structured, understandable, and relevant."},
    ]

    logical_bank = [
        {"question": "What number comes next in the sequence 3, 6, 12, 24, ...?", "options": ["30", "36", "48", "60"], "correct_option": "C", "explanation": "Each term is doubled, so 24 x 2 = 48."},
        {"question": "All roses are flowers. Some flowers fade quickly. Which statement must be true?", "options": ["All roses fade quickly", "Some roses fade quickly", "All roses are flowers", "No flowers are roses"], "correct_option": "C", "explanation": "The first statement directly establishes that all roses are flowers."},
        {"question": "If A is taller than B and B is taller than C, who is shortest?", "options": ["A", "B", "C", "Cannot be determined"], "correct_option": "C", "explanation": "The ordering is A > B > C, so C is shortest."},
        {"question": "Which item does not belong: square, triangle, circle, cube?", "options": ["Square", "Triangle", "Circle", "Cube"], "correct_option": "D", "explanation": "A cube is three-dimensional; the other choices are two-dimensional shapes."},
    ]

    reasoning_bank = [
        {"question": "A is the brother of B. B is the sister of C. How is A related to C?", "options": ["Brother", "Sister", "Father", "Cannot be determined"], "correct_option": "A", "explanation": "A and C are siblings, and A is explicitly identified as a brother."},
        {"question": "If today is Wednesday, what day will it be 10 days from today?", "options": ["Friday", "Saturday", "Sunday", "Monday"], "correct_option": "B", "explanation": "Ten days is one week plus three days; Wednesday plus three days is Saturday."},
        {"question": "A person walks 4 km north, then 3 km east. In which direction are they from the start?", "options": ["North-west", "South-east", "North-east", "South-west"], "correct_option": "C", "explanation": "Moving north and then east places the person north-east of the start."},
        {"question": "In a code, CAT is written as DBU by shifting each letter forward once. How is DOG written?", "options": ["EPH", "CNE", "FQI", "EOG"], "correct_option": "A", "explanation": "Each letter moves forward by one: D->E, O->P, G->H."},
    ]

    technical_bank = [
        {"question": "What does JVM stand for?", "options": ["Java Variable Machine", "Java Virtual Machine", "Java Version Method", "Java Virtual Memory"], "correct_option": "B", "explanation": "JVM runs Java bytecode."},
        {"question": "Which HTTP method is used to create a new resource in REST APIs?", "options": ["GET", "POST", "PUT", "DELETE"], "correct_option": "B", "explanation": "POST creates a new resource."},
        {"question": "Which of the following is a benefit of SQL indexes?", "options": ["Increase storage cost only", "Speed up read queries", "Delete duplicate rows automatically", "Prevent all updates"], "correct_option": "B", "explanation": "Indexes improve search performance on large tables."},
        {"question": "What is dependency injection mainly used for?", "options": ["To remove all classes", "To decouple components and improve testability", "To store data in HTML", "To replace the database"], "correct_option": "B", "explanation": "Dependency injection reduces coupling and better supports testing."},
        {"question": "Which layer commonly handles HTTP requests in a Spring Boot application?", "options": ["Repository", "Controller", "Model", "Database"], "correct_option": "B", "explanation": "Controller handles incoming HTTP traffic."},
        {"question": "What is the purpose of @Service in Spring Boot?", "options": ["To map HTTP routes", "To define business logic classes", "To store environment variables", "To connect CSS styles"], "correct_option": "B", "explanation": "@Service marks service layer classes for business logic."},
        {"question": "Which SQL keyword is used to filter rows?", "options": ["SELECT", "WHERE", "JOIN", "ORDER"], "correct_option": "B", "explanation": "WHERE filters records before returning them."},
        {"question": "What is the main advantage of using ORM frameworks like Hibernate?", "options": ["No database needed", "Simplifies DB mapping and query work", "Runs only in CSS", "Removes all Java code"], "correct_option": "B", "explanation": "ORM tools reduce manual mapping between Java objects and tables."},
        {"question": "What does REST stand for?", "options": ["Representational State Transfer", "Remote Execution Service Tool", "Relational Endpoint Storage Transfer", "Readable Event Service Template"], "correct_option": "A", "explanation": "REST is Representational State Transfer."},
        {"question": "Which of the following is a valid HTTP status code for success?", "options": ["200", "500", "404", "301"], "correct_option": "A", "explanation": "200 indicates a successful request."},
    ]

    coding_java_bank = [
        {"question": "Which Java collection provides O(1) average-time key lookup?", "options": ["ArrayList", "HashMap", "LinkedList", "Stack"], "correct_option": "B", "explanation": "HashMap provides fast key-based lookup."},
        {"question": "Which keyword is used to declare a class that cannot be extended?", "options": ["static", "final", "abstract", "protected"], "correct_option": "B", "explanation": "final classes cannot be subclassed."},
        {"question": "What is the correct way to reverse a String in Java?", "options": ["Collections.reverse()", "StringBuffer.reverse()", "Math.reverse()", "System.reverse()"], "correct_option": "B", "explanation": "StringBuilder/StringBuffer have reverse() method."},
        {"question": "Which of these is true about ArrayList?", "options": ["Fixed size", "Resizes dynamically", "Only stores unique values", "Thread-safe by default"], "correct_option": "B", "explanation": "ArrayList grows dynamically as items are added."},
        {"question": "Which of the following is used to handle multiple exceptions in Java?", "options": ["switch", "try-catch", "for-each", "interface"], "correct_option": "B", "explanation": "try-catch blocks handle exceptions."},
        {"question": "Which collection maintains insertion order?", "options": ["HashSet", "HashMap", "LinkedHashSet", "TreeSet"], "correct_option": "C", "explanation": "LinkedHashSet preserves insertion order."},
        {"question": "Which Java interface is implemented by ArrayList?", "options": ["Map", "Set", "List", "Queue"], "correct_option": "C", "explanation": "ArrayList implements the List interface."},
        {"question": "Which method is used to remove an element from a Java List?", "options": ["delete()", "remove()", "clearAll()", "drop()"], "correct_option": "B", "explanation": "remove() removes one element from a List."},
        {"question": "What is the default value of an uninitialized int field in a Java class?", "options": ["0", "null", "false", "undefined"], "correct_option": "A", "explanation": "Numeric fields default to 0."},
        {"question": "Which method is used to print output in Java?", "options": ["println()", "scan()", "read()", "write()"], "correct_option": "A", "explanation": "System.out.println() prints to console."},
    ]

    coding_python_bank = [
        {"question": "Which Python data structure is best for fast key lookup?", "options": ["List", "Tuple", "Dictionary", "Set"], "correct_option": "C", "explanation": "Dictionary provides fast key-based lookup."},
        {"question": "What is the output of len([1,2,3,4]) in Python?", "options": ["3", "4", "5", "None"], "correct_option": "B", "explanation": "The list contains 4 elements."},
        {"question": "Which of these is used to create a function in Python?", "options": ["function myfunc()", "def myfunc()", "func myfunc()", "method myfunc()"], "correct_option": "B", "explanation": "Python functions are defined with def."},
        {"question": "Which method sorts a list in place in Python?", "options": ["sorted()", "sort()", "order()", "arrange()"], "correct_option": "B", "explanation": "list.sort() sorts in place."},
        {"question": "Which collection is immutable by default in Python?", "options": ["list", "dict", "tuple", "set"], "correct_option": "C", "explanation": "Tuple is an immutable sequence."},
        {"question": "What does append() do on a Python list?", "options": ["Remove item", "Sort items", "Add item at the end", "Reverse letters"], "correct_option": "C", "explanation": "append() adds an item to the end of the list."},
        {"question": "Which expression checks if x is equal to 5 in Python?", "options": ["x = 5", "x == 5", "x != 5", "x < 5"], "correct_option": "B", "explanation": "== is comparison, while = is assignment."},
        {"question": "Which Python collection stores unique values only?", "options": ["list", "tuple", "set", "dict"], "correct_option": "C", "explanation": "A set contains unique elements."},
        {"question": "What is the result of 3 ** 2 in Python?", "options": ["5", "6", "9", "8"], "correct_option": "C", "explanation": "Exponentiation 3 ** 2 = 9."},
        {"question": "Which of these is the correct way to read user input in Python?", "options": ["input()", "read()", "scanf()", "console()"], "correct_option": "A", "explanation": "input() reads data from standard input."},
    ]

    coding_challenges = {
        "python": [
            {
                "question": "Write a Python function that returns the sum of two integers.",
                "starter_code": "def add_numbers(a, b):\n    # Write your code here\n    return 0\n",
                "function_name": "add_numbers",
                "language": "Python",
                "test_cases": [{"args": [2, 3], "expected": 5}, {"args": [10, 7], "expected": 17}, {"args": [-4, 9], "expected": 5}],
                "explanation": "Add the two input integers and return the result. The sample cases include positive and negative values; addition should work the same way for both. This can be solved in O(1) time and O(1) extra space."
            },
            {
                "question": "Write a Python function to find the largest number in a list.",
                "starter_code": "def max_number(numbers):\n    # Write your code here\n    return 0\n",
                "function_name": "max_number",
                "language": "Python",
                "test_cases": [{"args": [[1, 5, 9, 3]], "expected": 9}, {"args": [[7, 2, 11, 4]], "expected": 11}, {"args": [[-3, -8, -1]], "expected": -1}],
                "explanation": "Start with the first list value as the current maximum, then compare each remaining value and update the maximum when a larger value is found. Initializing from the list (rather than zero) also handles lists containing only negative numbers. This takes O(n) time and O(1) extra space."
            },
            {
                "question": "Write a Python function that returns True for even numbers and False for odd numbers.",
                "starter_code": "def is_even(number):\n    # Write your code here\n    return False\n",
                "function_name": "is_even",
                "language": "Python",
                "test_cases": [{"args": [2], "expected": True}, {"args": [7], "expected": False}, {"args": [0], "expected": True}],
                "explanation": "A number is even when its remainder after division by 2 is zero. Return a boolean for that condition; zero is even, while positive and negative odd numbers are not. This takes O(1) time and O(1) extra space."
            }
        ],
        "java": [
            {
                "question": "Write a Java method that returns the sum of two integers.",
                "starter_code": "public class Solution {\n    public static int addNumbers(int a, int b) {\n        // Write your code here\n        return 0;\n    }\n}",
                "function_name": "addNumbers",
                "language": "Java",
                "test_cases": [{"args": [2, 3], "expected": 5}, {"args": [10, 7], "expected": 17}, {"args": [-4, 9], "expected": 5}],
                "explanation": "Add the two input integers and return the result. The sample cases include positive and negative values; addition should work the same way for both. This can be solved in O(1) time and O(1) extra space."
            },
            {
                "question": "Write a Java method to find the largest number in an array.",
                "starter_code": "public class Solution {\n    public static int maxNumber(int[] numbers) {\n        // Write your code here\n        return 0;\n    }\n}",
                "function_name": "maxNumber",
                "language": "Java",
                "test_cases": [{"args": [[1, 5, 9, 3]], "expected": 9}, {"args": [[7, 2, 11, 4]], "expected": 11}, {"args": [[-3, -8, -1]], "expected": -1}],
                "explanation": "Start with the first array value as the current maximum, then compare each remaining value and update the maximum when a larger value is found. Initializing from the array (rather than zero) also handles arrays containing only negative numbers. This takes O(n) time and O(1) extra space."
            },
            {
                "question": "Write a Java method that checks whether a number is even.",
                "starter_code": "public class Solution {\n    public static boolean isEven(int number) {\n        // Write your code here\n        return false;\n    }\n}",
                "function_name": "isEven",
                "language": "Java",
                "test_cases": [{"args": [2], "expected": True}, {"args": [7], "expected": False}, {"args": [0], "expected": True}],
                "explanation": "A number is even when its remainder after division by 2 is zero. Return a boolean for that condition; zero is even, while positive and negative odd numbers are not. This takes O(1) time and O(1) extra space."
            }
        ]
    }

    def build_mcq(qset, category_label, topic_label):
        idx = (state.get("current_question") or 1) - 1
        choice = qset[idx % len(qset)]
        return {
            "question": f"{category_label}: {choice['question']}",
            "options": choice["options"],
            "correct_option": choice["correct_option"],
            "explanation": choice["explanation"],
            "category": category_label,
            "difficulty": state.get("difficulty", "Intermediate"),
            "topic": topic_label,
            "target_role": target_role,
            "question_number": state.get("current_question") or 1,
        }

    if interview_type == "aptitude":
        return build_mcq(aptitude_bank, "Aptitude", "Aptitude")
    if interview_type == "communication":
        return build_mcq(communication_bank, "Communication", "Communication")
    if interview_type == "logical":
        return build_mcq(logical_bank, "Logical Ability", "Logical Ability")
    if interview_type == "reasoning":
        return build_mcq(reasoning_bank, "Reasoning", "Reasoning")
    if interview_type == "coding":
        language_key = "java" if str(coding_language).lower().startswith("j") else "python"
        challenge = (coding_challenges.get(language_key) or coding_challenges["python"])[(state.get("current_question") - 1) % len(coding_challenges.get(language_key) or coding_challenges["python"])]
        return {
            "question": challenge["question"],
            "options": [],
            "correct_option": None,
            "explanation": challenge["explanation"],
            "category": "Coding",
            "difficulty": state.get("difficulty", "Intermediate"),
            "topic": f"Coding ({challenge['language']})",
            "target_role": target_role,
            "question_number": state.get("current_question") or 1,
            "question_type": "coding",
            "language": challenge["language"],
            "starter_code": challenge["starter_code"],
            "function_name": challenge.get("function_name"),
            "test_cases": challenge.get("test_cases", []),
        }

    return build_mcq(technical_bank, "Technical", "Technical")


def run_coding_challenge(language: str, code: str, challenge: Dict[str, Any]) -> Dict[str, Any]:
    lang = (language or "Python").lower()
    tests = challenge.get("test_cases") or []
    if not tests:
        return {"passed": False, "score": 0, "feedback": "No test cases available for this challenge.", "passed_cases": 0, "total_cases": 0, "output": ""}
    if "python" not in lang and "java" not in lang:
        return {"passed": False, "score": 0, "feedback": "Unsupported language for code execution.", "passed_cases": 0, "total_cases": len(tests), "output": ""}

    try:
        if "python" in lang:
            if not code or "def " not in code:
                return {"passed": False, "score": 0, "feedback": "Write a valid Python function before submitting.", "passed_cases": 0, "total_cases": len(tests), "output": ""}
            namespace: Dict[str, Any] = {}
            exec(code, namespace)
            function_name = challenge.get("function_name") or next((name for name in namespace if callable(namespace[name])), None)
            if not function_name or function_name not in namespace or not callable(namespace[function_name]):
                return {"passed": False, "score": 0, "feedback": "The function name in your code does not match the challenge requirement.", "passed_cases": 0, "total_cases": len(tests), "output": ""}
            passed_cases = 0
            output_lines = []
            for index, test_case in enumerate(tests, start=1):
                args = test_case.get("args") or []
                expected = test_case.get("expected")
                try:
                    result = namespace[function_name](*args)
                    if result == expected:
                        passed_cases += 1
                        output_lines.append(f"Case {index}: PASS")
                    else:
                        output_lines.append(f"Case {index}: FAIL (expected {expected}, got {result})")
                        continue
                except Exception as exc:
                    output_lines.append(f"Case {index}: ERROR ({exc})")
            score = round((passed_cases / len(tests)) * 10, 2)
            passed = passed_cases == len(tests)
            feedback = "All Python test cases passed successfully." if passed else f"Passed {passed_cases} out of {len(tests)} test cases."
            return {"passed": passed, "score": score, "feedback": feedback, "passed_cases": passed_cases, "total_cases": len(tests), "output": "\n".join(output_lines or ["Execution completed successfully."])}

        if "java" in lang:
            code_to_run = code.strip()
            if not code_to_run or "class Solution" not in code_to_run:
                return {"passed": False, "score": 0, "feedback": "Write a Java Solution class before submitting.", "passed_cases": 0, "total_cases": len(tests), "output": ""}
            with tempfile.TemporaryDirectory() as tmp_dir:
                source_path = Path(tmp_dir) / "Solution.java"
                method_name = str(challenge.get("function_name") or "addNumbers")
                args_lines = []
                for idx, test_case in enumerate(tests, start=1):
                    args = test_case.get("args") or []
                    expected = test_case.get("expected")
                    if isinstance(args, list) and len(args) == 1 and isinstance(args[0], list):
                        values = args[0]
                        java_literal = "new int[]{" + ", ".join(str(v) for v in values) + "}"
                        java_args = java_literal
                    else:
                        java_args = ", ".join(str(value) for value in args)
                    invocation = f"{method_name}({java_args})"
                    expected_literal = str(expected).lower() if isinstance(expected, bool) else str(expected)
                    args_lines.extend([
                        f"boolean __pass{idx} = ({invocation}) == ({expected_literal});",
                        f'System.out.println("CASE {idx}: " + (__pass{idx} ? "PASS" : "FAIL"));',
                    ])

                class_end = code_to_run.rfind("}")
                if class_end < 0:
                    return {"passed": False, "score": 0, "feedback": "The Java Solution class is missing its closing brace.", "passed_cases": 0, "total_cases": len(tests), "output": ""}
                harness = "\npublic static void main(String[] args) {\n" + "\n".join(args_lines) + "\n}\n"
                code_with_harness = code_to_run[:class_end] + harness + code_to_run[class_end:]
                source_path.write_text(code_with_harness, encoding="utf-8")
                compile_result = subprocess.run(["javac", str(source_path)], cwd=tmp_dir, capture_output=True, text=True, timeout=20)
                if compile_result.returncode != 0:
                    compiler_output = compile_result.stderr.strip() or compile_result.stdout.strip()
                    return {"passed": False, "score": 0, "feedback": f"Java compilation failed: {compiler_output}", "passed_cases": 0, "total_cases": len(tests), "output": compiler_output}
                run_result = subprocess.run(["java", "-cp", tmp_dir, "Solution"], cwd=tmp_dir, capture_output=True, text=True, timeout=10)
                if run_result.returncode != 0:
                    runtime_output = run_result.stderr.strip() or run_result.stdout.strip()
                    return {"passed": False, "score": 0, "feedback": f"Java runtime failed: {runtime_output}", "passed_cases": 0, "total_cases": len(tests), "output": runtime_output}
                stdout = (run_result.stdout or "").strip()
                passed_cases = sum(1 for line in stdout.splitlines() if line.startswith("CASE ") and line.endswith(": PASS"))
                score = round((passed_cases / len(tests)) * 10, 2)
                return {"passed": passed_cases == len(tests), "score": score, "feedback": f"Java execution completed. Passed {passed_cases}/{len(tests)} test cases.", "passed_cases": passed_cases, "total_cases": len(tests), "output": stdout}
    except Exception as exc:
        return {"passed": False, "score": 0, "feedback": f"Runner error: {exc}", "passed_cases": 0, "total_cases": len(tests), "output": ""}


def evaluate_answer(question: str, answer: str, candidate_profile: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    gemini = get_gemini_client()
    resume_context = json.dumps(candidate_profile or {}, ensure_ascii=False)
    prompt = f"""
    Evaluate this candidate answer in a rigorous but fair way.
    Question: {question}
    Candidate answer: {answer}
    Candidate profile: {resume_context}
    Return JSON only with keys:
    score, max_score, technical_correctness, completeness, relevance, clarity, strengths, weaknesses, missing_points, feedback, difficulty_for_next_question, topic, recommended_next_action.
    The score should be 0 to 10. Provide explicit reasoning in feedback and explain why it got that score.
    """
    try:
        if gemini and getattr(gemini, "available", False):
            result = gemini.generate_json(prompt)
            if isinstance(result, dict):
                normalized = {
                    "score": int(float(result.get("score", 7) or 7)),
                    "max_score": int(float(result.get("max_score", 10) or 10)),
                    "technical_correctness": int(float(result.get("technical_correctness", 7) or 7)),
                    "completeness": int(float(result.get("completeness", 7) or 7)),
                    "relevance": int(float(result.get("relevance", 7) or 7)),
                    "clarity": int(float(result.get("clarity", 7) or 7)),
                    "strengths": result.get("strengths") or ["Basic understanding of the concept was shown."],
                    "weaknesses": result.get("weaknesses") or ["Could add more concrete examples and technical depth."],
                    "missing_points": result.get("missing_points") or ["Deeper technical explanation"],
                    "feedback": result.get("feedback") or "Good start; include more technical depth and concrete examples.",
                    "difficulty_for_next_question": result.get("difficulty_for_next_question") or "medium",
                    "topic": result.get("topic") or _topic_from_question(question),
                    "recommended_next_action": result.get("recommended_next_action") or "moderate_followup",
                }
                return normalized
    except Exception as exc:
        logger.warning("Gemini answer evaluation failed: %s", exc)

    words = len(answer.split())
    score = 6
    if words > 40:
        score = 8
    elif words < 10:
        score = 4
    return {
        "score": score,
        "max_score": 10,
        "technical_correctness": min(10, max(3, score)),
        "completeness": min(10, max(3, score - 1)),
        "relevance": min(10, max(3, score + 1)),
        "clarity": min(10, max(3, score)),
        "strengths": ["Candidate attempted a direct answer to the question."],
        "weaknesses": ["More detailed reasoning and examples would improve the answer."],
        "missing_points": ["Technical details", "Concrete examples", "Trade-offs"],
        "feedback": "The answer shows some understanding but would be stronger with clearer structure, more technical precision, and examples tied to real-world usage.",
        "difficulty_for_next_question": "medium",
        "topic": _topic_from_question(question),
        "recommended_next_action": "moderate_followup",
    }


def adaptive_difficulty(previous_scores: List[int], current_difficulty: str) -> str:
    if not previous_scores:
        return current_difficulty
    avg = sum(previous_scores) / len(previous_scores)
    if avg > 80:
        return "Advanced"
    if avg >= 60:
        return "Intermediate"
    return "Beginner"


def summarize_topic_performance(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    scores: Dict[str, List[int]] = {}
    for item in history:
        topic = item.get("topic") or "General"
        score = item.get("evaluation", {}).get("score", 0)
        scores.setdefault(topic, []).append(int(score or 0))

    topic_scores = {}
    for topic, values in scores.items():
        avg = sum(values) / len(values) if values else 0
        topic_scores[topic] = round(avg * 10, 2)
    return topic_scores


def final_performance_report(state: Dict[str, Any]) -> Dict[str, Any]:
    history = state.get("question_history") or []
    scores = [int(item.get("score", 0) or 0) for item in history if isinstance(item, dict)]
    overall = round(sum(scores) / len(scores), 2) if scores else 0
    technical = round(sum(item.get("technical_score", 0) for item in history if isinstance(item, dict)) / max(1, len(history)), 2)
    communication = round(sum(item.get("clarity_score", 0) for item in history if isinstance(item, dict)) / max(1, len(history)), 2)
    problem_solving = round(sum(item.get("score", 0) for item in history if isinstance(item, dict)) / max(1, len(history)), 2)
    role_readiness = min(100, max(0, round(overall * 1.1, 2)))
    topic_scores = summarize_topic_performance(history)

    weak_topics = sorted(topic_scores.items(), key=lambda x: x[1])[:3]
    strengths = [topic for topic, value in sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]]
    weaknesses = [topic for topic, _ in weak_topics]
    recommendations = [
        f"Focus on improving {topic} with targeted practice and structured revision." for topic, _ in weak_topics
    ]
    learning_plan = []
    for idx, (topic, _) in enumerate(weak_topics, start=1):
        learning_plan.append({
            "day": idx,
            "topic": topic,
            "focus": f"Practice {topic} fundamentals and answer 3 scenario questions."
        })

    return {
        "overall_score": overall,
        "technical_score": technical,
        "communication_score": communication,
        "problem_solving_score": problem_solving,
        "role_readiness": role_readiness,
        "topic_scores": topic_scores,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "learning_plan": learning_plan,
        "weak_topics": weak_topics,
    }


class InterviewWorkflow:
    def __init__(self, profile: Dict[str, Any], target_role: str, interview_type: str, difficulty: str, total_questions: int, missing_skills: Optional[List[str]] = None):
        self.profile = profile or {}
        self.target_role = target_role
        self.interview_type = interview_type
        self.difficulty = difficulty
        self.total_questions = total_questions
        self.missing_skills = missing_skills or profile.get("missing_skills") or _extract_missing_skills(profile, target_role)
        self.state = {
            "candidate_profile": profile,
            "resume_context": profile,
            "target_role": target_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "question_count": total_questions,
            "current_question": 1,
            "question_history": [],
            "topic_scores": {},
            "weak_topics": [],
            "overall_score": 0,
            "interview_status": "active",
        }

    def run(self):
        if LANGGRAPH_AVAILABLE:
            graph = StateGraph(dict)
            graph.add_node("load_context", lambda state: {**state, **self._load_context()})
            graph.add_node("plan_interview", lambda state: {**state, **{"plan": plan_interview(state.get("candidate_profile", {}), state.get("target_role", self.target_role), state.get("interview_type", self.interview_type), state.get("difficulty", self.difficulty), state.get("question_count", self.total_questions))}})
            graph.add_node("generate_question", lambda state: {**state, **generate_question_for_session(state)})
            graph.add_node("final_analysis", lambda state: {**state, **{"report": final_performance_report(state)}})
            graph.set_entry_point("load_context")
            graph.add_edge("load_context", "plan_interview")
            graph.add_edge("plan_interview", "generate_question")
            graph.add_edge("generate_question", "final_analysis")
            compiled = graph.compile()
            return compiled.invoke(self.state)

        state = {**self.state, "plan": plan_interview(self.profile, self.target_role, self.interview_type, self.difficulty, self.total_questions)}
        question = generate_question_for_session(state)
        state["current_question"] = 1
        state["current_question_payload"] = question
        state["report"] = final_performance_report(state)
        return state

    def _load_context(self):
        return {
            "candidate_profile": self.profile,
            "resume_context": self.profile,
            "target_role": self.target_role,
            "interview_type": self.interview_type,
            "difficulty": self.difficulty,
            "question_count": self.total_questions,
            "missing_skills": self.missing_skills,
        }
