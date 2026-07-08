"""
CyberTech Academy — Seed Data Script
Run: python seed_data.py
"""
import os, sys, django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.courses.models import Category, Course, Module, Lesson
from apps.students.models import StudentProfile, Enrollment
from apps.zoom_sessions.models import ZoomSession

print("\n🚀 Seeding CyberTech Academy...\n")

# ── 1. SUPERADMIN ─────────────────────────────────────────────
admin, created = User.objects.get_or_create(
    email='admin@cybertech.ac',
    defaults=dict(
        username='admin', first_name='Super', last_name='Admin',
        role=User.Role.SUPERADMIN, is_staff=True, is_superuser=True,
        is_verified=True, country='Uganda',
    )
)
if created:
    admin.set_password('CyberAdmin2025!')
    admin.save()
print(f"  {'✅ Created' if created else '⏭  Exists '} Admin       → {admin.email}")

# ── 2. INSTRUCTORS ────────────────────────────────────────────
instructors_data = [
    dict(email='alex@cybertech.ac',  username='alex_instructor',
         first_name='Alex',  last_name='Mugisha',
         bio='Cybersecurity expert with 8 years in ethical hacking and network defence.',
         country='Uganda'),
    dict(email='sarah@cybertech.ac', username='sarah_instructor',
         first_name='Sarah', last_name='Nakato',
         bio='Full-stack developer & AI enthusiast. Builds production web apps for Ugandan startups.',
         country='Uganda'),
]
instructors = []
for d in instructors_data:
    u, created = User.objects.get_or_create(email=d['email'], defaults={
        **d, 'role': User.Role.INSTRUCTOR, 'is_verified': True
    })
    if created:
        u.set_password('Instructor2025!')
        u.save()
    instructors.append(u)
    print(f"  {'✅ Created' if created else '⏭  Exists '} Instructor  → {u.email}")

# ── 3. CATEGORIES ─────────────────────────────────────────────
categories_data = [
    ('Cybersecurity',         'cybersecurity',   'fas fa-shield-halved'),
    ('Web Development',       'web-development', 'fas fa-code'),
    ('Networking',            'networking',      'fas fa-network-wired'),
    ('AI & Machine Learning', 'ai-ml',           'fas fa-robot'),
    ('Cloud Computing',       'cloud-computing', 'fas fa-cloud'),
    ('Database Design',       'database-design', 'fas fa-database'),
]
cats = {}
for name, slug, icon in categories_data:
    cat, created = Category.objects.get_or_create(slug=slug, defaults={
        'name': name, 'icon': icon,
        'description': f'Learn {name} from industry experts.'
    })
    cats[slug] = cat
    print(f"  {'✅ Created' if created else '⏭  Exists '} Category    → {name}")

# ── 4. COURSES ────────────────────────────────────────────────
courses_data = [
    dict(
        title='Ethical Hacking & Penetration Testing',
        slug='ethical-hacking-penetration-testing',
        description='Master the art of ethical hacking. Learn reconnaissance, exploitation, post-exploitation, and reporting. Hands-on labs using Kali Linux.',
        category=cats['cybersecurity'],
        instructor=instructors[0],
        price=0, is_free=True,
        difficulty=Course.Difficulty.BEGINNER,
        duration_hours=20, is_published=True, is_featured=True,
        modules_data=[
            ('Introduction to Ethical Hacking', [
                ('What is Ethical Hacking?',      'video', 15, True),
                ('Legal & Ethical Framework',     'text',  10, False),
                ('Setting Up Kali Linux',         'video', 25, False),
            ]),
            ('Reconnaissance Techniques', [
                ('Passive Reconnaissance',        'video', 20, True),
                ('Active Scanning with Nmap',     'video', 30, False),
                ('OSINT Tools Overview',          'pdf',   15, False),
            ]),
            ('Exploitation Basics', [
                ('Metasploit Framework Intro',    'video', 35, False),
                ('Exploiting Common Vulnerabilities', 'video', 40, False),
                ('Module Quiz',                   'quiz',  20, False),
            ]),
        ]
    ),
    dict(
        title='Full-Stack Web Development with Django & React',
        slug='fullstack-django-react',
        description='Build production-ready web applications from scratch. Covers Django REST APIs, React frontend, PostgreSQL, and cloud deployment.',
        category=cats['web-development'],
        instructor=instructors[1],
        price=150000, is_free=False,
        difficulty=Course.Difficulty.INTERMEDIATE,
        duration_hours=35, is_published=True, is_featured=True,
        modules_data=[
            ('Django Foundations', [
                ('Django Project Setup',          'video', 20, True),
                ('Models & Migrations',           'video', 30, False),
                ('Django REST Framework',         'video', 25, False),
            ]),
            ('React Frontend', [
                ('React Hooks & State',           'video', 25, True),
                ('Axios & API Integration',       'video', 30, False),
                ('Tailwind CSS Styling',          'video', 20, False),
            ]),
            ('Deployment', [
                ('PostgreSQL Setup',              'video', 20, False),
                ('Deploying to Railway',          'video', 25, False),
                ('Final Project',                 'text',   0, False),
            ]),
        ]
    ),
    dict(
        title='CompTIA Network+ Exam Preparation',
        slug='comptia-network-plus-prep',
        description='Complete preparation for the CompTIA Network+ certification. OSI model, TCP/IP, routing, switching, and troubleshooting covered in depth.',
        category=cats['networking'],
        instructor=instructors[0],
        price=120000, is_free=False,
        difficulty=Course.Difficulty.BEGINNER,
        duration_hours=25, is_published=True, is_featured=False,
        modules_data=[
            ('Networking Fundamentals', [
                ('OSI Model Explained',           'video', 25, True),
                ('TCP/IP Suite',                  'video', 30, False),
                ('IP Addressing & Subnetting',    'video', 40, False),
            ]),
            ('Network Devices', [
                ('Routers vs Switches',           'video', 20, True),
                ('Firewalls & VPNs',              'video', 25, False),
                ('Wireless Networking',           'video', 30, False),
            ]),
        ]
    ),
    dict(
        title='Python for AI & Machine Learning',
        slug='python-ai-machine-learning',
        description='From Python basics to building real ML models. Covers NumPy, Pandas, scikit-learn, and TensorFlow with real-world Ugandan datasets.',
        category=cats['ai-ml'],
        instructor=instructors[1],
        price=200000, is_free=False,
        difficulty=Course.Difficulty.INTERMEDIATE,
        duration_hours=40, is_published=True, is_featured=True,
        modules_data=[
            ('Python for Data Science', [
                ('NumPy & Pandas Basics',         'video', 30, True),
                ('Data Visualisation',            'video', 25, False),
                ('Data Cleaning',                 'video', 20, False),
            ]),
            ('Machine Learning', [
                ('Supervised Learning',           'video', 35, True),
                ('Model Evaluation',              'video', 25, False),
                ('Neural Networks Intro',         'video', 40, False),
            ]),
        ]
    ),
    dict(
        title='AWS Cloud Practitioner Certification',
        slug='aws-cloud-practitioner',
        description='Prepare for the AWS Certified Cloud Practitioner exam. Covers core AWS services, security, pricing, and architecture best practices.',
        category=cats['cloud-computing'],
        instructor=instructors[0],
        price=0, is_free=True,
        difficulty=Course.Difficulty.BEGINNER,
        duration_hours=15, is_published=True, is_featured=False,
        modules_data=[
            ('AWS Fundamentals', [
                ('What is Cloud Computing?',      'video', 15, True),
                ('AWS Global Infrastructure',     'video', 20, False),
                ('IAM & Security',                'video', 25, False),
            ]),
        ]
    ),
    dict(
        title='MySQL & PostgreSQL for Developers',
        slug='mysql-postgresql-developers',
        description='Master relational databases from schema design to advanced queries, indexing, stored procedures, and performance optimisation.',
        category=cats['database-design'],
        instructor=instructors[1],
        price=80000, is_free=False,
        difficulty=Course.Difficulty.BEGINNER,
        duration_hours=18, is_published=True, is_featured=False,
        modules_data=[
            ('Database Design', [
                ('ER Diagrams & Normalisation',   'video', 25, True),
                ('CREATE TABLE & Constraints',    'video', 20, False),
                ('Relationships & Joins',         'video', 30, False),
            ]),
            ('Advanced SQL', [
                ('Subqueries & CTEs',             'video', 25, True),
                ('Indexing & Performance',        'video', 30, False),
                ('Stored Procedures',             'video', 25, False),
            ]),
        ]
    ),
]

course_objs = []
for cd in courses_data:
    modules_data = cd.pop('modules_data')
    course, created = Course.objects.get_or_create(slug=cd['slug'], defaults=cd)
    course_objs.append(course)
    print(f"  {'✅ Created' if created else '⏭  Exists '} Course      → {course.title}")

    if created:
        for m_order, (m_title, lessons) in enumerate(modules_data, 1):
            module = Module.objects.create(course=course, title=m_title, order=m_order)
            for l_order, (l_title, l_type, l_mins, l_preview) in enumerate(lessons, 1):
                Lesson.objects.create(
                    module=module, title=l_title,
                    content_type=l_type, order=l_order,
                    duration_minutes=l_mins,
                    is_preview=l_preview,
                    video_url='https://www.youtube.com/embed/dQw4w9WgXcQ' if l_type == 'video' else '',
                )

# ── 5. STUDENTS ───────────────────────────────────────────────
students_data = [
    dict(email='brian@student.com', username='brian_k', first_name='Brian',
         last_name='Kato',   country='Uganda',   phone='+256700001111'),
    dict(email='diana@student.com', username='diana_m', first_name='Diana',
         last_name='Mugabi', country='Uganda',   phone='+256700002222'),
    dict(email='peter@student.com', username='peter_o', first_name='Peter',
         last_name='Okello', country='Kenya',    phone='+254700003333'),
    dict(email='grace@student.com', username='grace_n', first_name='Grace',
         last_name='Nambi',  country='Tanzania', phone='+255700004444'),
]
student_objs = []
for d in students_data:
    u, created = User.objects.get_or_create(email=d['email'], defaults={
        **d, 'role': User.Role.STUDENT, 'is_verified': True,
        'is_active': True,   # already admitted for seed purposes
    })
    if created:
        u.set_password('Student2025!')
        u.save()
        StudentProfile.objects.create(
            user=u,
            course_interest=course_objs[0],
            learning_mode='both',
            terms_accepted=True,
            admission_status=StudentProfile.AdmissionStatus.ADMITTED,
            admission_fee_paid=True,
        )
    student_objs.append(u)
    print(f"  {'✅ Created' if created else '⏭  Exists '} Student     → {u.email}")

# ── 6. ENROLMENTS ─────────────────────────────────────────────
enrolments = [
    (student_objs[0], course_objs[0]),
    (student_objs[0], course_objs[4]),
    (student_objs[1], course_objs[1]),
    (student_objs[2], course_objs[0]),
    (student_objs[3], course_objs[3]),
]
for student, course in enrolments:
    enr, created = Enrollment.objects.get_or_create(student=student, course=course)
    print(f"  {'✅ Created' if created else '⏭  Exists '} Enrollment  → {student.first_name} in {course.title[:40]}")

# ── 7. ZOOM SESSIONS ──────────────────────────────────────────
sessions_data = [
    dict(
        title='Live: Advanced Ethical Hacking Workshop',
        description='Interactive 3-hour deep-dive into buffer overflow exploits, privilege escalation, and CTF challenges.',
        instructor=instructors[0],
        zoom_link='https://zoom.us/j/123456789?pwd=REPLACE_WITH_REAL_LINK',
        scheduled_at=timezone.now() + timedelta(days=5),
        duration_minutes=180, price=75000, max_participants=30, is_active=True,
    ),
    dict(
        title='Live: Build & Deploy a Django SaaS App',
        description='From zero to deployed in one session. Build a subscription SaaS with Django and deploy to Railway.',
        instructor=instructors[1],
        zoom_link='https://zoom.us/j/987654321?pwd=REPLACE_WITH_REAL_LINK',
        scheduled_at=timezone.now() + timedelta(days=12),
        duration_minutes=240, price=100000, max_participants=25, is_active=True,
    ),
    dict(
        title='Live: AI Career Masterclass — Opportunities in Uganda',
        description='Explore AI career paths, freelancing with ML skills, and landing remote AI jobs as a Ugandan developer.',
        instructor=instructors[1],
        zoom_link='https://zoom.us/j/555666777?pwd=REPLACE_WITH_REAL_LINK',
        scheduled_at=timezone.now() + timedelta(days=20),
        duration_minutes=120, price=50000, max_participants=50, is_active=True,
    ),
]
for sd in sessions_data:
    session, created = ZoomSession.objects.get_or_create(title=sd['title'], defaults=sd)
    print(f"  {'✅ Created' if created else '⏭  Exists '} ZoomSession → {session.title[:50]}")

print("\n✅ Seed complete!\n")
print("=" * 55)
print("  CREDENTIALS")
print("=" * 55)
print("  Admin      admin@cybertech.ac     CyberAdmin2025!")
print("  Instructor alex@cybertech.ac      Instructor2025!")
print("  Instructor sarah@cybertech.ac     Instructor2025!")
print("  Student    brian@student.com      Student2025!")
print("  Student    diana@student.com      Student2025!")
print("=" * 55)
print("  Admin Panel → http://127.0.0.1:8000/admin/")
print("  Site        → http://127.0.0.1:8000/")
print("=" * 55)