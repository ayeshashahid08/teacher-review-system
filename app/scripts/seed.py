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

# CLASSES = ["Grade 5A", "Grade 6B", "Grade 7C"]

GRADES = [
    {"grade_number": 1, "school_level": "primary"},
    {"grade_number": 2, "school_level": "primary"},
    {"grade_number": 3, "school_level": "primary"},
    {"grade_number": 4, "school_level": "primary"},
    {"grade_number": 5, "school_level": "primary"},
    {"grade_number": 6, "school_level": "secondary"},
    {"grade_number": 7, "school_level": "secondary"},
    {"grade_number": 8, "school_level": "secondary"},
    {"grade_number": 9, "school_level": "higher_secondary"},
    {"grade_number": 10, "school_level": "higher_secondary"},
    {"grade_number": 11, "school_level": "higher_secondary"},
    {"grade_number": 12, "school_level": "higher_secondary"},
]

DIVISIONS_BY_GRADE = {
    1: ["A", "B", "C", "D"],
    2: ["A", "B", "C", "D"],
    3: ["A", "B", "C", "D"],
    4: ["A", "B", "C", "D"],
    5: ["A", "B", "C", "D"],
    6: ["A", "B", "C", "D"],
    7: ["A", "B", "C", "D"],
    8: ["A", "B", "C"],
    9: ["A", "B", "C"],
    10: ["A", "B", "C"],
    11: ["A", "B", "C"],
    12: ["A", "B", "C"],
}

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
    # ("Academics", "Performance Beyond Class", "Is up to date with routine checking work."),
    # ("Academics", "Performance Beyond Class", "Has good level of satisfaction as per master checker's record."),
    # ("Academics", "Performance Beyond Class", "Maintains good quality of paper setting."),
    # ("Academics", "Performance Beyond Class", "Maintains good quality of paper checking."),
    # ("Academics", "Performance Beyond Class", "Makes results timely."),
    # ("Academics", "Performance Beyond Class", "Meets deadlines."),
    # ("Academics", "Performance Beyond Class", "Maintains all registers and planners."),
    # ("Academics", "Performance Beyond Class", "Extends cooperation when any extra task is assigned."),
    ("Teacher-Student Relationship", "Academics", "Creates an environment that is positive for students."),
    ("Teacher-Student Relationship", "Academics", "Strives to ensure equitable opportunities for students."),
    ("Teacher-Student Relationship", "Academics", "Organizes class to encourage collaborative learning."),
    ("Teacher-Student Relationship", "Academics", "Promotes confidence and perseverance in students."),
]

ACR_QUESTIONS = [

    # ============================================================
    # 1. ACADEMICS
    # ============================================================

    # A. In Class Performance
    (
        "Academics",
        "In Class Performance",
        """Effectively plans instruction and assessment making learning goals clear to students.
Enters fully prepared for the class.
Follows lesson plans.
Maintains a good learning atmosphere; adequate use of audio/visual aids and other tools.
Is able to analyze/assess and change teaching techniques/tools as per students' interests/scenarios.
Utilizes proxy time efficiently.
Invigilates as per expectation."""
    ),

    # B. Performance Beyond Class
    (
        "Academics",
        "Performance Beyond Class",
        """Is up to date with routine checking work.
Has good level of satisfaction as per master checker's record.
Maintains good quality of paper setting.
Maintains good quality of paper checking.
Makes results timely.
Meets deadlines.
Maintains all registers and planners.
Extends cooperation when any extra task is assigned."""
    ),


    # ============================================================
    # 2. TEACHER–STUDENT RELATIONSHIP
    # ============================================================

    # A. Academics
    (
        "Teacher-Student Relationship",
        "Academics",
        """Creates an environment that is positive for students and assists them to develop creative constructive behavior.
Strives to ensure equitable opportunities for students in an unbiased manner whether students belong to her own class or other.
Organizes class to encourage students for collaborative learning.
Promotes confidence and perseverance in students for achieving the goals of the curriculum."""
    ),

    # B. Beyond Academics
    (
        "Teacher-Student Relationship",
        "Beyond Academics",
        """Encourages/motivates for co/extracurricular activities including assembly presentations.
Keeps record of participation of students.
Counsels students for rowdy behavior.
Uses trainings provided for creating discipline.
Is concerned for overall atmosphere and culture of the school."""
    ),


    # ============================================================
    # 3. TEACHER–TEACHER RELATIONSHIP
    # ============================================================

    (
        "Teacher-Teacher Relationship",
        None,
        """Shares ideas, materials and methods with other teachers.
Uses praise, acceptance and humor when needed thus cultivating an atmosphere of positive relations.
Goes out of the ways to provide support and cooperation to peers when required.
Works with team spirit while carrying out extra-curricular activities and ensures program effectiveness."""
    ),


    # ============================================================
    # 4. TEACHER–MANAGEMENT RELATIONSHIP
    # ============================================================

    (
        "Teacher-Management Relationship",
        None,
        """Gives importance to co-ordination meetings and takes them seriously.
Participates enthusiastically in In-school/Out-school workshops.
Follows instructions for a constructive output and fulfills responsibilities.
Accepts suggestions/criticism.
Consults supervisors when needs advice.
Offers suggestions for improvement through proper channels.
Talks positively on every platform about the school.
Is wise enough to discuss the problems/drawbacks to the concerned person.
Stands with the management for the events organized by the management/top management."""
    ),


    # ============================================================
    # 5. TEACHER–INTRA PERSONAL
    # ============================================================

    (
        "Teacher-Intra Personal",
        None,
        """Believes in a growth mindset and not a fixed mindset (both in intellect and behavior).
Adopts different ways to improve intellect and behavior (such as reading, YouTube/Google search, TED talks and study circles).
Knows his/her strengths and weaknesses.
Is emotionally balanced in showing expressions.
Shows confidence in proving his/her mettle."""
    ),


    # ============================================================
    # 6. TEACHER–PERSONAL ATTRIBUTES
    # ============================================================

    (
        "Teacher-Personal Attributes",
        None,
        """Dresses as per dress code and maintains overall appearance as per policy.
Performs duties (Miscellaneous) well.
Shows honesty, integrity and truthfulness.
Is sincere towards students and institution.
Responds positively to parents' queries, suggestions and complaints.
Uses mobile phone constructively.
Enjoys work.
Uses decent language.
Is an organized person; maintains drawers, lockers, cupboards etc. well."""
    ),


    # ============================================================
    # 7. REGULARITY AND PUNCTUALITY
    # ============================================================

    (
        "Regularity and Punctuality",
        None,
        """Doesn't take unplanned leaves.
Doesn't take uninformed leaves.
Doesn't take frequent short leaves/half days.
Doesn't get absent on Mondays.
Doesn't get absent on Activity days/Exam days.
Doesn't come late.
Doesn't go on leave after a long vacation."""
    ),
]

ACR_MARKS = {
    ("Academics", "In Class Performance"): 20,
    ("Academics", "Performance Beyond Class"): 20,
    ("Teacher-Student Relationship", "Academics"): 20,
    ("Teacher-Student Relationship", "Beyond Academics"): 10,
    ("Teacher-Teacher Relationship", None): 15,
    ("Teacher-Management Relationship", None): 15,
    ("Teacher-Intra Personal", None): 10,
    ("Teacher-Personal Attributes", None): 10,
    ("Regularity and Punctuality", None): 20,
}


ACR_OVERALL_GRADES = [
    (90, 100, "A+"),
    (80, 89.99, "A"),
    (70, 79.99, "B"),
    (60, 69.99, "C"),
    (0, 59.99, "D"),
]

TEACHER_ASSIGNMENTS = [
    {"email": "teacher1@school.com", "subject_name": "Mathematics", "grade_number": 5, "division": "A", "classes_per_week": 5},
    {"email": "teacher1@school.com", "subject_name": "Mathematics", "grade_number": 6, "division": "B", "classes_per_week": 3},
    {"email": "teacher2@school.com", "subject_name": "English", "grade_number": 5, "division": "A", "classes_per_week": 4},
    {"email": "teacher2@school.com", "subject_name": "Science", "grade_number": 7, "division": "C", "classes_per_week": 3},
    {"email": "chiefcoord@school.com", "subject_name": "Urdu", "grade_number": 6, "division": "B", "classes_per_week": 2},
    {"email": "peercoord@school.com", "subject_name": "Science", "grade_number": 5, "division": "A", "classes_per_week": 3},
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

        # print("Seeding classes...")
        # for name in CLASSES:
        #     if not db.query(Class).filter(Class.class_name == name).first():
        #         db.add(Class(class_name=name))
        # db.commit()
        print("Seeding class yearly strength...")
        all_classes = db.query(Class).all()
        for class_ in all_classes:
            existing = db.query(ClassYearlyStrength).filter(
                ClassYearlyStrength.class_id == class_.class_id,
                ClassYearlyStrength.academic_year == ACADEMIC_YEAR
            ).first()
            if not existing:
                db.add(ClassYearlyStrength(
                    class_id=class_.class_id,
                    academic_year=ACADEMIC_YEAR,
                    strength=30  # default strength, admin can update later via endpoint
                ))
        db.commit()

        # print("Seeding class yearly strength...")
        # for entry in CLASS_STRENGTHS:
        #     class_ = db.query(Class).filter(Class.class_name == entry["class_name"]).first()
        #     if class_:
        #         existing = db.query(ClassYearlyStrength).filter(
        #             ClassYearlyStrength.class_id == class_.class_id,
        #             ClassYearlyStrength.academic_year == ACADEMIC_YEAR
        #         ).first()
        #         if not existing:
        #             db.add(ClassYearlyStrength(
        #                 class_id=class_.class_id,
        #                 academic_year=ACADEMIC_YEAR,
        #                 strength=entry["strength"]
        #             ))
        # db.commit()

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

        # print("Seeding ACR questions and grade criteria...")
        # for question_text, max_marks in ACR_QUESTIONS:
        #     existing_q = db.query(QuestionBank).filter(
        #         QuestionBank.question_text == question_text
        #     ).first()
        #     if not existing_q:
        #         new_q = QuestionBank(
        #             question_type="acr",
        #             question_text=question_text,
        #             is_active=True,
        #             created_by=admin.user_id,
        #             max_points=max_marks,
        #         )
        #         db.add(new_q)
        #         db.flush()

        #         for grade, (min_m, max_m) in zip(
        #             ["A+", "A", "B", "C"],
        #             [
        #                 (int(max_marks * 0.85), max_marks),
        #                 (int(max_marks * 0.70), int(max_marks * 0.84)),
        #                 (int(max_marks * 0.55), int(max_marks * 0.69)),
        #                 (0, int(max_marks * 0.54)),
        #             ]
        #         ):
        #             db.add(ACRGradeCriteria(
        #                 acr_question_id=new_q.question_id,
        #                 min_marks=min_m,
        #                 max_marks=max_m,
        #                 grade=grade,
        #             ))
        # db.commit()

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

        print("Seeding grades...")
        from app.models.grade import Grade

        for g in GRADES:
            if not db.query(Grade).filter(Grade.grade_number == g["grade_number"]).first():
                db.add(Grade(grade_number=g["grade_number"], school_level=g["school_level"]))
        db.commit()

        print("Seeding classes...")
        for grade_number, divisions in DIVISIONS_BY_GRADE.items():
            grade = db.query(Grade).filter(Grade.grade_number == grade_number).first()
            for division in divisions:
                if not db.query(Class).filter(
                    Class.grade_id == grade.grade_id,
                    Class.division == division
                ).first():
                    db.add(Class(grade_id=grade.grade_id, division=division))
        db.commit()

        print("Seeding teacher assignments...")
        

        for assignment in TEACHER_ASSIGNMENTS:
            from app.models.grade import Grade

            user = db.query(User).filter(User.email == assignment["email"]).first()
            subject = db.query(Subject).filter(Subject.subject_name == assignment["subject_name"]).first()
            grade = db.query(Grade).filter(Grade.grade_number == assignment["grade_number"]).first()
            class_ = db.query(Class).filter(
                Class.grade_id == grade.grade_id,
                Class.division == assignment["division"]
            ).first() if grade else None

            if not user or not subject or not class_:
                print(f"Skipping assignment - missing data for {assignment}")
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
