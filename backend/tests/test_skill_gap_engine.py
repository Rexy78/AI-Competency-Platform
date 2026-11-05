from app.ai.skill_gap_engine import analyze_skill_gaps
from app.ai.parser import extract_resume_skills, extract_skills_from_text


def test_missing_oop_is_high_priority():
    result = analyze_skill_gaps(["Java", "SQL", "Git"], "Java Backend Developer")

    oop_gap = next(item for item in result["gap_matrix"] if item["skill"] == "OOP")
    oop_recommendation = next(
        item for item in result["recommendations"] if item["skill"] == "OOP"
    )

    assert oop_gap["status"] == "Missing"
    assert oop_gap["priority"] == "High"
    assert oop_recommendation["priority"] == "High"


def test_object_oriented_programming_in_resume_matches_oop_requirement():
    for wording in ("Object-Oriented Programming", "OOPs"):
        skills = extract_skills_from_text(f"Experienced in Java and {wording}.")
        result = analyze_skill_gaps(skills, "Java Backend Developer")

        oop_gap = next(item for item in result["gap_matrix"] if item["skill"] == "OOP")
        assert oop_gap["status"] == "Available"


def test_similar_skill_names_do_not_match_different_requirements():
    result = analyze_skill_gaps(["JavaScript", "Spring"], "Java Backend Developer")
    statuses = {item["skill"]: item["status"] for item in result["gap_matrix"]}

    assert statuses["Java"] == "Missing"
    assert statuses["Spring Boot"] == "Missing"


def test_saved_resume_raw_text_repairs_old_extracted_skill_list():
    parsed_resume = {
        "all_skills": ["Java"],
        "raw_text": "Java developer with Object-Oriented Programming experience.",
    }

    result = analyze_skill_gaps(extract_resume_skills(parsed_resume), "Java Backend Developer")
    oop_gap = next(item for item in result["gap_matrix"] if item["skill"] == "OOP")

    assert oop_gap["status"] == "Available"


def test_mysql_matches_sql_requirement():
    result = analyze_skill_gaps(["MySQL"], "Java Backend Developer")
    sql_gap = next(item for item in result["gap_matrix"] if item["skill"] == "SQL")

    assert sql_gap["status"] == "Available"
