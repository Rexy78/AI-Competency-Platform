from app.ai.skill_gap_engine import analyze_skill_gaps


def test_missing_oop_is_high_priority():
    result = analyze_skill_gaps(["Java", "SQL", "Git"], "Java Backend Developer")

    oop_gap = next(item for item in result["gap_matrix"] if item["skill"] == "OOP")
    oop_recommendation = next(
        item for item in result["recommendations"] if item["skill"] == "OOP"
    )

    assert oop_gap["status"] == "Missing"
    assert oop_gap["priority"] == "High"
    assert oop_recommendation["priority"] == "High"
