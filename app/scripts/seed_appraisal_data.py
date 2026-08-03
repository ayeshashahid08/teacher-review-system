from app.database import SessionLocal
from app.models.question import QuestionBank, QuestionOption
from app.models.acr import ACROverallGradeCriteria  # adjust import to your actual file

ADMIN_USER_ID = 1  # replace with a real admin/HR user_id from your users table

MCQ_OPTIONS = [
    {"option_grade": "A+", "score_value": 1.0},
    {"option_grade": "A", "score_value": 0.75},
    {"option_grade": "B", "score_value": 0.5},
    {"option_grade": "C", "score_value": 0.25},
]

# (section, subsection, question_text) — only sections visible in the screenshot (page 1).
# Add the remaining bullets from page 2 following the same pattern.
QUESTIONS = [
    ("Academics", "In Class Performance", "Effectively plans instruction and assessment making learning goals clear to students."),
    ("Academics", "In Class Performance", "Enters fully prepared for the class."),
    ("Academics", "In Class Performance", "Follows lesson plans."),
    ("Academics", "In Class Performance", "Maintains a good learning atmosphere; adequate use of audio/visual aids and other tools."),
    ("Academics", "In Class Performance", "Is able to analyze/assess and change teaching techniques/tools as per students' interests/scenarios."),
    ("Academics", "In Class Performance", "Utilizes proxy time efficiently."),
    ("Academics", "In Class Performance", "Invigilates as per expectation."),

    ("Academics", "Performance Beyond Class", "Is up to date with routine checking work."),
    ("Academics", "Performance Beyond Class", "Has good level of satisfaction as per master checker's record."),
    ("Academics", "Performance Beyond Class", "Maintains good quality of paper setting."),
    ("Academics", "Performance Beyond Class", "Maintains good quality of paper checking."),
    ("Academics", "Performance Beyond Class", "Makes results timely."),
    ("Academics", "Performance Beyond Class", "Meets deadlines."),
    ("Academics", "Performance Beyond Class", "Maintains all registers and planners."),
    ("Academics", "Performance Beyond Class", "Extends cooperation when any extra task is assigned."),

    ("Teacher-Student Relationship", "Academics", "Creates an environment that is positive for students and assists to develop creative constructive behavior."),
    ("Teacher-Student Relationship", "Academics", "Strives to ensure equitable opportunities for students in an unbiased manner whether students belong to her own class or other."),
    ("Teacher-Student Relationship", "Academics", "Organizes class to encourage students for collaborative learning."),
    ("Teacher-Student Relationship", "Academics", "Promotes confidence and perseverance in students for achieving the goals of the curriculum."),
    # continues on page 2 — add remaining bullets here
]

GRADE_BANDS = [
    (90, 100, "A+ Grade Teacher"),
    (80, 89.99, "A Grade Teacher"),
    (70, 79.99, "B Grade Teacher"),
    (60, 69.99, "C Grade Teacher"),
]


def seed():
    db = SessionLocal()
    try:
        for opt in MCQ_OPTIONS:
            if not db.query(QuestionOption).filter(QuestionOption.option_grade == opt["option_grade"]).first():
                db.add(QuestionOption(**opt))
        db.commit()

        for section, subsection, text in QUESTIONS:
            if not db.query(QuestionBank).filter(QuestionBank.question_text == text).first():
                db.add(QuestionBank(
                    question_type="observation",
                    question_text=text,
                    section=section,
                    subsection=subsection,
                    max_points=1,
                    is_active=True,
                    created_by=ADMIN_USER_ID,
                ))
        db.commit()

        for min_p, max_p, grade in GRADE_BANDS:
            if not db.query(ACROverallGradeCriteria).filter(ACROverallGradeCriteria.grade == grade).first():
                db.add(ACROverallGradeCriteria(min_percentage=min_p, max_percentage=max_p, grade=grade))
        db.commit()

        print(f"Seeded {len(MCQ_OPTIONS)} options, {len(QUESTIONS)} questions, {len(GRADE_BANDS)} grade bands.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()