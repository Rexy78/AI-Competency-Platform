from app.ai.agentic_interview import generate_question_for_session, run_coding_challenge
from app.routes.interview import _section_question_plan


def test_full_practice_ends_with_two_coding_questions():
    sections = ["communication", "aptitude", "logical", "reasoning", "technical", "coding"]

    question_plan = _section_question_plan(sections, 62)

    assert len(question_plan) == 62
    assert question_plan[-2:] == ["coding", "coding"]
    assert question_plan.index("coding") == 60


def test_logical_and_reasoning_sections_generate_mcqs():
    for section, expected_category in [
        ("logical", "Logical Ability"),
        ("reasoning", "Reasoning"),
    ]:
        question = generate_question_for_session({
            "interview_type": section,
            "current_question": 1,
            "difficulty": "Intermediate",
        })

        assert question["category"] == expected_category
        assert len(question["options"]) == 4
        assert question["correct_option"] in {"A", "B", "C", "D"}


def test_coding_questions_use_selected_language():
    for language, expected_starter in [
        ("Python", "def "),
        ("Java", "public class Solution"),
    ]:
        question = generate_question_for_session({
            "interview_type": "coding",
            "coding_language": language,
            "current_question": 61,
        })

        assert question["question_type"] == "coding"
        assert question["language"] == language
        assert question["starter_code"].startswith(expected_starter)
        assert question["explanation"]
        assert question["test_cases"]


def test_all_python_coding_challenges_run():
    solutions = [
        "def add_numbers(a, b):\n    return a + b\n",
        "def max_number(numbers):\n    return max(numbers)\n",
        "def is_even(number):\n    return number % 2 == 0\n",
    ]

    for question_number, solution in enumerate(solutions, start=1):
        challenge = generate_question_for_session({
            "interview_type": "coding",
            "coding_language": "Python",
            "current_question": question_number,
        })
        result = run_coding_challenge("Python", solution, challenge)

        assert result["passed"] is True, result
        assert result["passed_cases"] == result["total_cases"] == 3


def test_all_java_coding_challenges_compile_and_run():
    solutions = [
        "public class Solution {\n    public static int addNumbers(int a, int b) {\n        return a + b;\n    }\n}",
        "public class Solution {\n    public static int maxNumber(int[] numbers) {\n        int max = numbers[0];\n        for (int number : numbers) max = Math.max(max, number);\n        return max;\n    }\n}",
        "public class Solution {\n    public static boolean isEven(int number) {\n        return number % 2 == 0;\n    }\n}",
    ]

    for question_number, solution in enumerate(solutions, start=1):
        challenge = generate_question_for_session({
            "interview_type": "coding",
            "coding_language": "Java",
            "current_question": question_number,
        })
        result = run_coding_challenge("Java", solution, challenge)

        assert result["passed"] is True, result
        assert result["passed_cases"] == result["total_cases"] == 3
