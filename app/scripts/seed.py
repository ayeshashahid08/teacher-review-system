from app.database import SessionLocal
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.class_yearly_strength import ClassYearlyStrength
from app.models.academic_year_settings import AcademicYearSettings
from app.models.question import QuestionBank, QuestionOption
from app.models.acr import ACROverallGradeCriteria, ACRGradeCriteria
from app.models.teacher_assignment import TeacherAssignment
from app.core.security import hash_password
from sqlalchemy import func

ACADEMIC_YEAR = "2025-2026"

USERS = [
    {
        "first_name": "System",
        "last_name": "Admin",
        "email": "admin@school.com",
        "password": "Admin123!",
        "designation": "admin",
        "is_active": True,
        "must_change_password": False,
        "employment_number": 9999,
        "CNIC": "9999999999999",
    },
    {
        "first_name": "Sara",
        "last_name": "Ahmed",
        "email": "principal@school.com",
        "password": "Admin123!",
        "designation": "principal",
        "is_active": True,
        "must_change_password": True,
        "employment_number": 1001,
        "CNIC": "1234567890001",
    },
    {
        "first_name": "Bilal",
        "last_name": "Khan",
        "email": "chiefcoord@school.com",
        "password": "Admin123!",
        "designation": "chief_coordinator",
        "is_active": True,
        "must_change_password": True,
        "employment_number": 1002,
        "CNIC": "1234567890002",
    },
    {
        "first_name": "Nadia",
        "last_name": "Ali",
        "email": "peercoord@school.com",
        "password": "Admin123!",
        "designation": "peer_coordinator",
        "is_active": True,
        "must_change_password": True,
        "employment_number": 1003,
        "CNIC": "1234567890003",
    },
    {
        "first_name": "Hassan",
        "last_name": "Malik",
        "email": "teacher1@school.com",
        "password": "Admin123!",
        "designation": "teacher",
        "is_active": True,
        "must_change_password": True,
        "employment_number": 1004,
        "CNIC": "1234567890004",
    },
    {
        "first_name": "Ayesha",
        "last_name": "Raza",
        "email": "teacher2@school.com",
        "password": "Admin123!",
        "designation": "teacher",
        "is_active": True,
        "must_change_password": True,
        "employment_number": 1005,
        "CNIC": "1234567890005",
    },
]

SUBJECTS = ["Mathematics", "English", "Science", "Urdu"]

CLASSES = ["Grade 5A", "Grade 6B", "Grade 7C"]

CLASS_STRENGTHS = [
    {"class_name": "Grade 5A", "strength": 30},
    {"class_name": "Grade 6B", "strength": 28},
    {"class_name": "Grade 7C", "strength": 25},
]

MCQ_OPTIONS = [
    {"option_grade": "A+", "score_value": 1.0},
    {"option_grade": "A", "score_value": 0.75},
    {"option_grade": "B", "score_value": 0.5},
    {"option_grade": "C", "score_value": 0.25},
]

OBSERVATION_QUESTIONS = [
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
    ("Teacher-Student Relationship", "Academics", "Creates an environment that is positive for students."),
    ("Teacher-Student Relationship", "Academics", "Strives to ensure equitable opportunities for students."),
    ("Teacher-Student Relationship", "Academics", "Organizes class to encourage collaborative learning."),
    ("Teacher-Student Relationship", "Academics", "Promotes confidence and perseverance in students."),
]

ACR_QUESTIONS = [
    ("Punctuality and attendance", 20),
    ("Quality of lesson planning", 20),
    ("Classroom management", 20),
    ("Student engagement", 20),
    ("Professional conduct", 20),
]

ACR_OVERALL_GRADES = [
    (90, 100, "A+"),
    (80, 89.99, "A"),
    (70, 79.99, "B"),
    (60, 69.99, "C"),
    (0, 59.99, "D"),
]

TEACHER_ASSIGNMENTS = [
    {"email": "teacher1@school.com", "subject_name": "Mathematics", "class_name": "Grade 5A", "classes_per_week": 5},
    {"email": "teacher1@school.com", "subject_name": "Mathematics", "class_name": "Grade 6B", "classes_per_week": 3},
    {"email": "teacher2@school.com", "subject_name": "English", "class_name": "Grade 5A", "classes_per_week": 4},
    {"email": "teacher2@school.com", "subject_name": "Science", "class_name": "Grade 7C", "classes_per_week": 3},
    {"email": "chiefcoord@school.com", "subject_name": "Urdu", "class_name": "Grade 6B", "classes_per_week": 2},
    {"email": "peercoord@school.com", "subject_name": "Science", "class_name": "Grade 5A", "classes_per_week": 3},
]

def seed():
    db = SessionLocal()
    try:
        print("Seeding users...")
        for u in USERS:
            if not db.query(User).filter(User.email == u["email"]).first():
                db.add(User(
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    designation=u["designation"],
                    is_active=u["is_active"],
                    must_change_password=u["must_change_password"],
                    employment_number=u["employment_number"],
                    CNIC=u["CNIC"],
                ))
        db.commit()

        print("Seeding academic year...")
        if not db.query(AcademicYearSettings).filter(
            AcademicYearSettings.academic_year == ACADEMIC_YEAR
        ).first():
            db.add(AcademicYearSettings(
                academic_year=ACADEMIC_YEAR,
                total_working_days=200
            ))
        db.commit()

        print("Seeding subjects...")
        for name in SUBJECTS:
            if not db.query(Subject).filter(Subject.subject_name == name).first():
                db.add(Subject(subject_name=name))
        db.commit()

        print("Seeding classes...")
        for name in CLASSES:
            if not db.query(Class).filter(Class.class_name == name).first():
                db.add(Class(class_name=name))
        db.commit()

        print("Seeding class yearly strength...")
        for entry in CLASS_STRENGTHS:
            class_ = db.query(Class).filter(Class.class_name == entry["class_name"]).first()
            if class_:
                existing = db.query(ClassYearlyStrength).filter(
                    ClassYearlyStrength.class_id == class_.class_id,
                    ClassYearlyStrength.academic_year == ACADEMIC_YEAR
                ).first()
                if not existing:
                    db.add(ClassYearlyStrength(
                        class_id=class_.class_id,
                        academic_year=ACADEMIC_YEAR,
                        strength=entry["strength"]
                    ))
        db.commit()

        print("Seeding MCQ options...")
        for opt in MCQ_OPTIONS:
            if not db.query(QuestionOption).filter(
                QuestionOption.option_grade == opt["option_grade"]
            ).first():
                db.add(QuestionOption(**opt))
        db.commit()

        print("Seeding observation questions...")
        admin = db.query(User).filter(User.email == "admin@school.com").first()
        for section, subsection, text in OBSERVATION_QUESTIONS:
            if not db.query(QuestionBank).filter(QuestionBank.question_text == text).first():
                db.add(QuestionBank(
                    question_type="observation",
                    question_text=text,
                    section=section,
                    subsection=subsection,
                    max_points=1,
                    is_active=True,
                    created_by=admin.user_id,
                ))
        db.commit()

        print("Seeding ACR questions and grade criteria...")
        for question_text, max_marks in ACR_QUESTIONS:
            existing_q = db.query(QuestionBank).filter(
                QuestionBank.question_text == question_text
            ).first()
            if not existing_q:
                new_q = QuestionBank(
                    question_type="acr",
                    question_text=question_text,
                    is_active=True,
                    created_by=admin.user_id,
                    max_points=max_marks,
                )
                db.add(new_q)
                db.flush()

                for grade, (min_m, max_m) in zip(
                    ["A+", "A", "B", "C"],
                    [
                        (int(max_marks * 0.85), max_marks),
                        (int(max_marks * 0.70), int(max_marks * 0.84)),
                        (int(max_marks * 0.55), int(max_marks * 0.69)),
                        (0, int(max_marks * 0.54)),
                    ]
                ):
                    db.add(ACRGradeCriteria(
                        acr_question_id=new_q.question_id,
                        min_marks=min_m,
                        max_marks=max_m,
                        grade=grade,
                    ))
        db.commit()

        print("Seeding ACR overall grade criteria...")
        for min_p, max_p, grade in ACR_OVERALL_GRADES:
            if not db.query(ACROverallGradeCriteria).filter(
                ACROverallGradeCriteria.grade == grade
            ).first():
                db.add(ACROverallGradeCriteria(
                    min_percentage=min_p,
                    max_percentage=max_p,
                    grade=grade
                ))
        db.commit()

        print("Seeding teacher assignments...")
        

        for assignment in TEACHER_ASSIGNMENTS:
            user = db.query(User).filter(User.email == assignment["email"]).first()
            subject = db.query(Subject).filter(Subject.subject_name == assignment["subject_name"]).first()
            class_ = db.query(Class).filter(Class.class_name == assignment["class_name"]).first()

            if not user or not subject or not class_:
                print(f"Skipping assignment - missing user/subject/class for {assignment}")
                continue

            existing = db.query(TeacherAssignment).filter(
                TeacherAssignment.user_id == user.user_id,
                TeacherAssignment.subject_id == subject.subject_id,
                TeacherAssignment.class_id == class_.class_id
            ).first()

            if not existing:
                db.add(TeacherAssignment(
                    user_id=user.user_id,
                    subject_id=subject.subject_id,
                    class_id=class_.class_id,
                    classes_per_week=assignment["classes_per_week"]
                ))

        db.commit()

        # recalculate teaching load for all assigned teachers
        print("Calculating teaching loads...")
        teachers = db.query(User).filter(
            User.designation.in_(["teacher", "coordinator", "peer_coordinator", "chief_coordinator"])
        ).all()

        for teacher in teachers:
            total = db.query(func.sum(TeacherAssignment.classes_per_week)).filter(
                TeacherAssignment.user_id == teacher.user_id
            ).scalar() or 0
            teacher.teaching_load = total

        db.commit()
        print("Teaching loads updated.")

        print("All data seeded successfully.")
        print("Admin login: admin@school.com / Admin123!")
        print("Principal login: principal@school.com / Admin123!")
        print("Chief Coordinator login: chiefcoord@school.com / Admin123!")
        print("Peer Coordinator login: peercoord@school.com / Admin123!")
        print("Teacher 1 login: teacher1@school.com / Admin123!")
        print("Teacher 2 login: teacher2@school.com / Admin123!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
