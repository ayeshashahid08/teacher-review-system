from app.database import SessionLocal
from app.models.user import User
from app.models.subject import Subject
from app.models.class_ import Class
from app.models.grade import Grade
from app.models.class_yearly_strength import ClassYearlyStrength
from app.models.academic_year_settings import AcademicYearSettings
from app.models.question import QuestionBank, QuestionOption
from app.models.acr import ACROverallGradeCriteria, ACRGradeCriteria
from app.models.teacher_assignment import TeacherAssignment
from app.models.coordinator_assignment import CoordinatorAssignment
from app.core.security import hash_password
from sqlalchemy import func

ACADEMIC_YEAR = "2026-2027"

USERS = [
    # System
    {
        "first_name": "System", "last_name": "Admin",
        "email": "admin@school.com", "password": "Admin123!",
        "designation": "admin", "must_change_password": False,
        "employment_number": 9999, "CNIC": "9999999999999",
    },
    # Principal
    {
        "first_name": "Sara", "last_name": "Ahmed",
        "email": "sara.ahmed@school.com", "password": "Admin123!",
        "designation": "principal", "must_change_password": True,
        "employment_number": 1001, "CNIC": "1234567890001",
    },

    # ==================== CHIEF COORDINATORS ====================
    {
        "first_name": "Bilal", "last_name": "Khan",
        "email": "bilal.khan@school.com", "password": "Admin123!",
        "designation": "teacher", "must_change_password": True,
        "employment_number": 1002, "CNIC": "1234567890002",
    },
    {
        "first_name": "Nadia", "last_name": "Ali",
        "email": "nadia.ali@school.com", "password": "Admin123!",
        "designation": "teacher", "must_change_password": True,
        "employment_number": 1003, "CNIC": "1234567890003",
    },

    # ==================== PEER COORDINATORS (Grade 1-10 + 11/12) ====================
    # Grade 1
    {"first_name": "Amina", "last_name": "Yousaf", "email": "amina.yousaf@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1101, "CNIC": "1234567890101"},
    # Grade 2
    {"first_name": "Fatima", "last_name": "Siddiqui", "email": "fatima.siddiqui@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1102, "CNIC": "1234567890102"},
    # Grade 3
    {"first_name": "Hassan", "last_name": "Malik", "email": "hassan.malik@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1103, "CNIC": "1234567890103"},
    # Grade 4
    {"first_name": "Zainab", "last_name": "Rashid", "email": "zainab.rashid@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1104, "CNIC": "1234567890104"},
    # Grade 5
    {"first_name": "Usman", "last_name": "Farooq", "email": "usman.farooq@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1105, "CNIC": "1234567890105"},
    # Grade 6
    {"first_name": "Sana", "last_name": "Iqbal", "email": "sana.iqbal@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1106, "CNIC": "1234567890106"},
    # Grade 7
    {"first_name": "Omar", "last_name": "Sheikh", "email": "omar.sheikh@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1107, "CNIC": "1234567890107"},
    # Grade 8
    {"first_name": "Ayesha", "last_name": "Raza", "email": "ayesha.raza@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1108, "CNIC": "1234567890108"},
    # Grade 9
    {"first_name": "Imran", "last_name": "Shah", "email": "imran.shah@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1109, "CNIC": "1234567890109"},
    # Grade 10
    {"first_name": "Hira", "last_name": "Nawaz", "email": "hira.nawaz@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1110, "CNIC": "1234567890110"},
    # Grade 11 + 12 (one person for both)
    {"first_name": "Kamran", "last_name": "Mehmood", "email": "kamran.mehmood@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1111, "CNIC": "1234567890111"},

    # ==================== SUBJECT COORDINATORS (Secondary only) ====================
    # Some overlap with peer coordinators is intentional
    {"first_name": "Sara", "last_name": "Khan", "email": "sara.khan@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1201, "CNIC": "1234567890201"},  # Math
    {"first_name": "Ali", "last_name": "Raza", "email": "ali.raza@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1202, "CNIC": "1234567890202"},  # English
    {"first_name": "Nida", "last_name": "Ahmed", "email": "nida.ahmed@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1203, "CNIC": "1234567890203"},  # Science
    {"first_name": "Faisal", "last_name": "Hussain", "email": "faisal.hussain@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1204, "CNIC": "1234567890204"},  # Urdu
    {"first_name": "Maryam", "last_name": "Zafar", "email": "maryam.zafar@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1205, "CNIC": "1234567890205"},  # Islamiat
    {"first_name": "Tariq", "last_name": "Javed", "email": "tariq.javed@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1206, "CNIC": "1234567890206"},  # Social Studies

    # ==================== REGULAR TEACHERS ====================
    {"first_name": "Teacher", "last_name": "One", "email": "teacher1@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1301, "CNIC": "1234567890301"},
    {"first_name": "Teacher", "last_name": "Two", "email": "teacher2@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1302, "CNIC": "1234567890302"},
    {"first_name": "Teacher", "last_name": "Three", "email": "teacher3@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1303, "CNIC": "1234567890303"},
    {"first_name": "Teacher", "last_name": "Four", "email": "teacher4@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1304, "CNIC": "1234567890304"},
    {"first_name": "Teacher", "last_name": "Five", "email": "teacher5@school.com", "password": "Admin123!",
     "designation": "teacher", "must_change_password": True, "employment_number": 1305, "CNIC": "1234567890305"},
]

SUBJECTS = ["Mathematics", "English", "Science", "Urdu", "Islamiat", "Social Studies"]

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

# ==================== TEACHER ASSIGNMENTS ====================
# Format: (email, subject, grade, division, classes_per_week)
TEACHER_ASSIGNMENTS = [
    # ---- Peer Coordinators also teaching ----
    ("amina.yousaf@school.com", "English", 1, "A", 5),
    ("amina.yousaf@school.com", "English", 1, "B", 5),
    ("fatima.siddiqui@school.com", "Urdu", 2, "A", 5),
    ("fatima.siddiqui@school.com", "Urdu", 2, "B", 4),
    ("hassan.malik@school.com", "Mathematics", 3, "A", 5),
    ("hassan.malik@school.com", "Mathematics", 3, "B", 5),
    ("zainab.rashid@school.com", "Science", 4, "A", 4),
    ("zainab.rashid@school.com", "Science", 4, "B", 4),
    ("usman.farooq@school.com", "Social Studies", 5, "A", 4),
    ("usman.farooq@school.com", "Social Studies", 5, "B", 4),

    # Secondary peer coords
    ("sana.iqbal@school.com", "English", 6, "A", 4),
    ("sana.iqbal@school.com", "English", 6, "B", 4),
    ("omar.sheikh@school.com", "Mathematics", 7, "A", 4),   # also Subject Coord Math
    ("omar.sheikh@school.com", "Mathematics", 7, "B", 4),
    ("ayesha.raza@school.com", "English", 8, "A", 4),        # also Subject Coord English
    ("ayesha.raza@school.com", "English", 8, "B", 3),
    ("imran.shah@school.com", "Science", 9, "A", 4),
    ("imran.shah@school.com", "Science", 9, "B", 3),
    ("hira.nawaz@school.com", "Urdu", 10, "A", 4),
    ("hira.nawaz@school.com", "Urdu", 10, "B", 3),
    ("kamran.mehmood@school.com", "Mathematics", 11, "A", 4),
    ("kamran.mehmood@school.com", "Mathematics", 12, "A", 4),

    # ---- Subject Coordinators teaching ----
    ("sara.khan@school.com", "Mathematics", 6, "C", 4),
    ("sara.khan@school.com", "Mathematics", 8, "A", 4),
    ("ali.raza@school.com", "English", 7, "A", 4),
    ("ali.raza@school.com", "English", 9, "A", 3),
    ("nida.ahmed@school.com", "Science", 6, "A", 4),
    ("nida.ahmed@school.com", "Science", 8, "B", 3),
    ("faisal.hussain@school.com", "Urdu", 7, "B", 4),
    ("faisal.hussain@school.com", "Urdu", 9, "B", 3),
    ("maryam.zafar@school.com", "Islamiat", 6, "A", 3),
    ("maryam.zafar@school.com", "Islamiat", 8, "A", 3),
    ("tariq.javed@school.com", "Social Studies", 7, "A", 3),
    ("tariq.javed@school.com", "Social Studies", 10, "A", 3),

    # ---- Regular teachers ----
    ("teacher1@school.com", "Science", 6, "B", 3),
    ("teacher1@school.com", "Science", 7, "C", 3),
    ("teacher2@school.com", "Islamiat", 5, "A", 4),
    ("teacher2@school.com", "Islamiat", 5, "B", 4),
    ("teacher3@school.com", "Mathematics", 9, "C", 4),
    ("teacher3@school.com", "Mathematics", 10, "B", 4),
    ("teacher4@school.com", "English", 11, "B", 3),
    ("teacher4@school.com", "English", 12, "B", 3),
    ("teacher5@school.com", "Social Studies", 4, "C", 3),
    ("teacher5@school.com", "Social Studies", 8, "C", 3),

    # Chiefs also teaching a little
    ("bilal.khan@school.com", "Social Studies", 3, "A", 2),
    ("nadia.ali@school.com", "Islamiat", 7, "A", 2),
]

# ==================== COORDINATOR ASSIGNMENTS ====================
# Format: (email, coordinator_type, grade_number, subject_name)
COORDINATOR_ASSIGNMENTS = [
    # ---- Chief Coordinators ----
    ("bilal.khan@school.com", "chief_primary", None, None),
    ("nadia.ali@school.com", "chief_secondary", None, None),

    # ---- Peer Coordinators (Grade 1-10) ----
    ("amina.yousaf@school.com", "peer", 1, None),
    ("fatima.siddiqui@school.com", "peer", 2, None),
    ("hassan.malik@school.com", "peer", 3, None),
    ("zainab.rashid@school.com", "peer", 4, None),
    ("usman.farooq@school.com", "peer", 5, None),
    ("sana.iqbal@school.com", "peer", 6, None),
    ("omar.sheikh@school.com", "peer", 7, None),      # also Subject Coord Math
    ("ayesha.raza@school.com", "peer", 8, None),      # also Subject Coord English
    ("imran.shah@school.com", "peer", 9, None),
    ("hira.nawaz@school.com", "peer", 10, None),

    # ---- Peer Coordinator for Grade 11 + 12 (same person) ----
    ("kamran.mehmood@school.com", "peer", 11, None),
    ("kamran.mehmood@school.com", "peer", 12, None),

    # ---- Subject Coordinators (Secondary only) ----
    ("sara.khan@school.com", "subject", None, "Mathematics"),
    ("ali.raza@school.com", "subject", None, "English"),
    ("nida.ahmed@school.com", "subject", None, "Science"),
    ("faisal.hussain@school.com", "subject", None, "Urdu"),
    ("maryam.zafar@school.com", "subject", None, "Islamiat"),
    ("tariq.javed@school.com", "subject", None, "Social Studies"),

    # Overlap examples (already peer + subject)
    ("omar.sheikh@school.com", "subject", None, "Mathematics"),   # peer of grade 7 + Math subject coord
    ("ayesha.raza@school.com", "subject", None, "English"),        # peer of grade 8 + English subject coord
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
    ("Teacher-Student Relationship", "Academics", "Creates an environment that is positive for students."),
    ("Teacher-Student Relationship", "Academics", "Strives to ensure equitable opportunities for students."),
    ("Teacher-Student Relationship", "Academics", "Organizes class to encourage collaborative learning."),
    ("Teacher-Student Relationship", "Academics", "Promotes confidence and perseverance in students."),
]

ACR_QUESTIONS = [
    (
        "Academics", "In Class Performance",
        """Effectively plans instruction and assessment making learning goals clear to students.
Enters fully prepared for the class.
Follows lesson plans.
Maintains a good learning atmosphere; adequate use of audio/visual aids and other tools.
Is able to analyze/assess and change teaching techniques/tools as per students' interests/scenarios.
Utilizes proxy time efficiently.
Invigilates as per expectation."""
    ),
    (
        "Academics", "Performance Beyond Class",
        """Is up to date with routine checking work.
Has good level of satisfaction as per master checker's record.
Maintains good quality of paper setting.
Maintains good quality of paper checking.
Makes results timely.
Meets deadlines.
Maintains all registers and planners.
Extends cooperation when any extra task is assigned."""
    ),
    (
        "Teacher-Student Relationship", "Academics",
        """Creates an environment that is positive for students and assists them to develop creative constructive behavior.
Strives to ensure equitable opportunities for students in an unbiased manner whether students belong to her own class or other.
Organizes class to encourage students for collaborative learning.
Promotes confidence and perseverance in students for achieving the goals of the curriculum."""
    ),
    (
        "Teacher-Student Relationship", "Beyond Academics",
        """Encourages/motivates for co/extracurricular activities including assembly presentations.
Keeps record of participation of students.
Counsels students for rowdy behavior.
Uses trainings provided for creating discipline.
Is concerned for overall atmosphere and culture of the school."""
    ),
    (
        "Teacher-Teacher Relationship", None,
        """Shares ideas, materials and methods with other teachers.
Uses praise, acceptance and humor when needed thus cultivating an atmosphere of positive relations.
Goes out of the ways to provide support and cooperation to peers when required.
Works with team spirit while carrying out extra-curricular activities and ensures program effectiveness."""
    ),
    (
        "Teacher-Management Relationship", None,
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
    (
        "Teacher-Intra Personal", None,
        """Believes in a growth mindset and not a fixed mindset (both in intellect and behavior).
Adopts different ways to improve intellect and behavior (such as reading, YouTube/Google search, TED talks and study circles).
Knows his/her strengths and weaknesses.
Is emotionally balanced in showing expressions.
Shows confidence in proving his/her mettle."""
    ),
    (
        "Teacher-Personal Attributes", None,
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
    (
        "Regularity and Punctuality", None,
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
                    is_active=True,
                    must_change_password=u["must_change_password"],
                    employment_number=u["employment_number"],
                    CNIC=u["CNIC"],
                ))
        db.commit()
        print(f"→ {len(USERS)} users seeded")

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

        print("Seeding grades...")
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

        print("Seeding class yearly strength...")
        all_classes = db.query(Class).all()
        for class_ in all_classes:
            if not db.query(ClassYearlyStrength).filter(
                ClassYearlyStrength.class_id == class_.class_id,
                ClassYearlyStrength.academic_year == ACADEMIC_YEAR
            ).first():
                db.add(ClassYearlyStrength(
                    class_id=class_.class_id,
                    academic_year=ACADEMIC_YEAR,
                    strength=30
                ))
        db.commit()

        print("Seeding MCQ options...")
        for opt in MCQ_OPTIONS:
            if not db.query(QuestionOption).filter(
                QuestionOption.option_grade == opt["option_grade"]
            ).first():
                db.add(QuestionOption(**opt))
        db.commit()

        # ---------- Observation Questions ----------
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

        # ---------- ACR Questions + Grade Criteria ----------
        print("Seeding ACR questions and grade criteria...")
        for section, subsection, text in ACR_QUESTIONS:
            existing = db.query(QuestionBank).filter(QuestionBank.question_text == text).first()
            if not existing:
                max_marks = ACR_MARKS.get((section, subsection), 10)
                question = QuestionBank(
                    question_type="acr",
                    section=section,
                    subsection=subsection,
                    question_text=text,
                    max_points=max_marks,
                    is_active=True,
                    created_by=admin.user_id,
                )
                db.add(question)
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
                        acr_question_id=question.question_id,
                        min_marks=min_m,
                        max_marks=max_m,
                        grade=grade,
                    ))
        db.commit()
        print("→ ACR questions + criteria seeded")

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

        # ---------- Teacher Assignments ----------
        print("Seeding teacher assignments...")
        for email, subject_name, grade_number, division, cpw in TEACHER_ASSIGNMENTS:
            user = db.query(User).filter(User.email == email).first()
            subject = db.query(Subject).filter(Subject.subject_name == subject_name).first()
            grade = db.query(Grade).filter(Grade.grade_number == grade_number).first()
            class_ = None
            if grade:
                class_ = db.query(Class).filter(
                    Class.grade_id == grade.grade_id,
                    Class.division == division
                ).first()

            if not user or not subject or not class_:
                print(f"  Skipping: {email} | {subject_name} | Grade {grade_number}{division}")
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
                    classes_per_week=cpw
                ))
        db.commit()

        print("Recalculating teaching loads...")
        all_teachers = db.query(User).filter(User.designation == "teacher").all()
        for teacher in all_teachers:
            total = db.query(func.sum(TeacherAssignment.classes_per_week)).filter(
                TeacherAssignment.user_id == teacher.user_id
            ).scalar() or 0
            teacher.teaching_load = total
        db.commit()

        # ---------- Coordinator Assignments ----------
        print("Seeding coordinator assignments...")
        for email, coord_type, grade_number, subject_name in COORDINATOR_ASSIGNMENTS:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                print(f"  User not found: {email}")
                continue

            grade_id = None
            subject_id = None

            if grade_number is not None:
                grade = db.query(Grade).filter(Grade.grade_number == grade_number).first()
                grade_id = grade.grade_id if grade else None

            if subject_name:
                subject = db.query(Subject).filter(Subject.subject_name == subject_name).first()
                subject_id = subject.subject_id if subject else None

            existing = db.query(CoordinatorAssignment).filter(
                CoordinatorAssignment.user_id == user.user_id,
                CoordinatorAssignment.coordinator_type == coord_type,
                CoordinatorAssignment.grade_id == grade_id,
                CoordinatorAssignment.subject_id == subject_id
            ).first()

            if not existing:
                db.add(CoordinatorAssignment(
                    user_id=user.user_id,
                    coordinator_type=coord_type,
                    grade_id=grade_id,
                    subject_id=subject_id
                ))
        db.commit()

        print("\n" + "="*60)
        print("ALL DATA SEEDED SUCCESSFULLY")
        print("="*60)
        print("\nLogin credentials (password for all: Admin123!):\n")
        print("Admin:              admin@school.com")
        print("Principal:          sara.ahmed@school.com")
        print("Chief Primary:      bilal.khan@school.com")
        print("Chief Secondary:    nadia.ali@school.com")
        print()
        print("Peer Coordinators:")
        print("  Grade 1:          amina.yousaf@school.com")
        print("  Grade 2:          fatima.siddiqui@school.com")
        print("  Grade 3:          hassan.malik@school.com")
        print("  Grade 4:          zainab.rashid@school.com")
        print("  Grade 5:          usman.farooq@school.com")
        print("  Grade 6:          sana.iqbal@school.com")
        print("  Grade 7:          omar.sheikh@school.com   ← also Subject Coord (Math)")
        print("  Grade 8:          ayesha.raza@school.com   ← also Subject Coord (English)")
        print("  Grade 9:          imran.shah@school.com")
        print("  Grade 10:         hira.nawaz@school.com")
        print("  Grade 11+12:      kamran.mehmood@school.com")
        print()
        print("Subject Coordinators (Secondary):")
        print("  Mathematics:      sara.khan@school.com + omar.sheikh@school.com")
        print("  English:          ali.raza@school.com + ayesha.raza@school.com")
        print("  Science:          nida.ahmed@school.com")
        print("  Urdu:             faisal.hussain@school.com")
        print("  Islamiat:         maryam.zafar@school.com")
        print("  Social Studies:   tariq.javed@school.com")
        print()
        print("Regular teachers: teacher1@school.com → teacher5@school.com")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()