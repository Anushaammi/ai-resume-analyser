from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Avg

import re
import os

from .models import ResumeAnalysis

import fitz
from docx import Document

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit


# ============================================================
# SKILL DETECTION
# ============================================================

def detect_skills(text):

    text_lower = text.lower()

    skills = {
        "Python": r"\bpython\b",
        "Java": r"\bjava\b",
        "JavaScript": r"\bjavascript\b",
        "HTML": r"\bhtml\b",
        "CSS": r"\bcss\b",
        "SQL": r"\bsql\b",
        "Django": r"\bdjango\b",
        "Flask": r"\bflask\b",
        "React": r"\breact\b",
        "Node.js": r"\bnode\.?js\b",
        "Git": r"\bgit\b",
        "GitHub": r"\bgithub\b",
        "Machine Learning": r"\bmachine learning\b",
        "Data Science": r"\bdata science\b",
        "C++": r"\bc\+\+\b",
        "C": r"\bc\b",
        "Bootstrap": r"\bbootstrap\b",
        "REST API": r"\brest api\b",
        "MongoDB": r"\bmongodb\b",
        "MySQL": r"\bmysql\b",
        "PostgreSQL": r"\bpostgresql\b",
        "Angular": r"\bangular\b",
        "TypeScript": r"\btypescript\b",
        "Pandas": r"\bpandas\b",
        "NumPy": r"\bnumpy\b",
        "TensorFlow": r"\btensorflow\b",
        "PyTorch": r"\bpytorch\b",
    }

    detected = []

    for skill, pattern in skills.items():

        if re.search(pattern, text_lower):

            if skill not in detected:
                detected.append(skill)

    return detected


# ============================================================
# RESUME SCORE
# ============================================================

def calculate_resume_score(text):

    score = 0
    text_lower = text.lower()

    # Resume sections
    sections = [
        "education",
        "skills",
        "projects",
        "experience",
        "certifications",
    ]

    for section in sections:

        if section in text_lower:
            score += 10

    # Email
    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text):
        score += 5

    # Phone number
    if re.search(r"\b\d{10}\b", text):
        score += 5

    # Resume length
    if len(text.split()) >= 300:
        score += 10

    # LinkedIn
    if "linkedin.com" in text_lower:
        score += 5

    # GitHub
    if "github.com" in text_lower:
        score += 5

    # Projects
    if "project" in text_lower:
        score += 5

    # Experience
    if "experience" in text_lower:
        score += 5

    # Certifications
    if "certification" in text_lower:
        score += 5

    # Skills
    detected_skills = detect_skills(text)

    if len(detected_skills) >= 3:
        score += 5

    if len(detected_skills) >= 6:
        score += 5

    if len(detected_skills) >= 10:
        score += 5

    return min(score, 100)


# ============================================================
# RESUME CATEGORY
# ============================================================

def detect_resume_category(skills):

    skill_set = set(skills)

    if "Python" in skill_set and "Django" in skill_set:
        return "Python Full Stack Developer"

    if "Java" in skill_set and "Spring" in skill_set:
        return "Java Full Stack Developer"

    if "Django" in skill_set:
        return "Django Developer"

    if "React" in skill_set:
        return "React Developer"

    if "Machine Learning" in skill_set:
        return "Machine Learning Developer"

    if "Data Science" in skill_set:
        return "Data Scientist"

    if "Python" in skill_set:
        return "Python Developer"

    if "Java" in skill_set:
        return "Java Developer"

    if "SQL" in skill_set:
        return "SQL Developer"

    return "General IT"


# ============================================================
# JOB SKILLS
# ============================================================

def find_job_skills(category):

    job_skill_map = {

        "Python Full Stack Developer": [
            "Python",
            "Django",
            "HTML",
            "CSS",
            "JavaScript",
            "SQL",
            "Git",
            "GitHub",
            "REST API",
        ],

        "Java Full Stack Developer": [
            "Java",
            "HTML",
            "CSS",
            "JavaScript",
            "SQL",
            "Git",
            "GitHub",
        ],

        "Django Developer": [
            "Python",
            "Django",
            "HTML",
            "CSS",
            "JavaScript",
            "SQL",
            "Git",
            "GitHub",
            "REST API",
        ],

        "React Developer": [
            "JavaScript",
            "React",
            "HTML",
            "CSS",
            "Git",
            "GitHub",
            "REST API",
        ],

        "Machine Learning Developer": [
            "Python",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "TensorFlow",
            "SQL",
        ],

        "Data Scientist": [
            "Python",
            "Data Science",
            "Pandas",
            "NumPy",
            "SQL",
            "Machine Learning",
        ],

        "Python Developer": [
            "Python",
            "SQL",
            "Git",
            "GitHub",
        ],

        "Java Developer": [
            "Java",
            "SQL",
            "Git",
            "GitHub",
        ],

        "SQL Developer": [
            "SQL",
            "MySQL",
            "PostgreSQL",
            "Git",
        ],

        "General IT": [
            "Python",
            "Java",
            "HTML",
            "CSS",
            "SQL",
            "Git",
        ],
    }

    return job_skill_map.get(
        category,
        job_skill_map["General IT"]
    )


# ============================================================
# JOB MATCHING
# ============================================================

def match_job(detected_skills, job_skills):

    detected_set = set(detected_skills)
    job_set = set(job_skills)

    matched = sorted(
        detected_set.intersection(job_set)
    )

    missing = sorted(
        job_set.difference(detected_set)
    )

    if len(job_set) == 0:
        percentage = 0
    else:
        percentage = round(
            (len(matched) / len(job_set)) * 100
        )

    return matched, missing, percentage


# ============================================================
# SUGGESTIONS
# ============================================================

def generate_suggestions(
    text,
    detected_skills,
    missing_skills=None
):

    text_lower = text.lower()

    suggestions = []

    # General suggestions

    if "experience" not in text_lower:
        suggestions.append(
            "Add relevant internship or experience details if applicable."
        )

    if "project" not in text_lower:
        suggestions.append(
            "Add practical projects with your role, technologies, and results."
        )

    if "certification" not in text_lower:
        suggestions.append(
            "Add relevant certifications if you have completed any."
        )

    if len(detected_skills) < 5:
        suggestions.append(
            "Mention your relevant technical skills clearly in a dedicated Skills section."
        )

    # Missing skills

    if missing_skills:

        suggestions.append(
            "Review the missing job-related skills below and add only the technologies you genuinely know or have used."
        )

    # Specific skill suggestions

    if "Django" in missing_skills if missing_skills else False:

        suggestions.append(
            "For Django roles, strengthen your knowledge of models, views, templates, URLs, forms, authentication, and REST APIs."
        )

    if "JavaScript" in missing_skills if missing_skills else False:

        suggestions.append(
            "Add JavaScript experience if you have worked with DOM manipulation, events, APIs, or frontend interactions."
        )

    if "HTML" in missing_skills if missing_skills else False:

        suggestions.append(
            "Include HTML experience such as forms, semantic elements, tables, and responsive page structure."
        )

    if "CSS" in missing_skills if missing_skills else False:

        suggestions.append(
            "Include CSS experience such as Flexbox, Grid, responsive design, and Bootstrap if applicable."
        )

    if "Git" in missing_skills if missing_skills else False:

        suggestions.append(
            "Mention Git experience if you use version control for your projects."
        )

    if "GitHub" in missing_skills if missing_skills else False:

        suggestions.append(
            "Add your GitHub profile and relevant project repositories if available."
        )

    if "REST API" in missing_skills if missing_skills else False:

        suggestions.append(
            "Learn and mention REST API development if you have practical experience with API creation or consumption."
        )

    if "React" in missing_skills if missing_skills else False:

        suggestions.append(
            "For frontend roles, strengthen React fundamentals such as components, props, state, hooks, and API integration."
        )

    if "SQL" in missing_skills if missing_skills else False:

        suggestions.append(
            "Add SQL experience including joins, subqueries, grouping, and database operations if applicable."
        )

    if "Python" in missing_skills if missing_skills else False:

        suggestions.append(
            "Highlight Python programming experience and relevant Python projects if applicable."
        )

    if "Java" in missing_skills if missing_skills else False:

        suggestions.append(
            "Highlight Java programming concepts and Java projects if applicable."
        )

    # Profile suggestions

    if "linkedin.com" not in text_lower:

        suggestions.append(
            "Add your LinkedIn profile URL to your resume."
        )

    if "github.com" not in text_lower:

        suggestions.append(
            "Add your GitHub profile URL if you have relevant repositories."
        )

    return suggestions


# ============================================================
# FILE TEXT EXTRACTION
# ============================================================

def extract_text_from_file(file):

    filename = file.name.lower()

    # PDF
    if filename.endswith(".pdf"):

        text = ""

        pdf = fitz.open(
            stream=file.read(),
            filetype="pdf"
        )

        for page in pdf:
            text += page.get_text()

        pdf.close()

        return text

    # DOCX
    elif filename.endswith(".docx"):

        document = Document(file)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

    # TXT
    elif filename.endswith(".txt"):

        return file.read().decode(
            "utf-8",
            errors="ignore"
        )

    return ""


# ============================================================
# HOME / RESUME ANALYSIS
# ============================================================

@login_required
def home(request):

    if request.method == "POST":

        uploaded_file = request.FILES.get(
            "resume"
        )

        job_description = request.POST.get(
            "job_description",
            ""
        ).strip()

        if not uploaded_file:

            messages.error(
                request,
                "Please upload a resume."
            )

            return redirect("home")

        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt",
        ]

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in allowed_extensions:

            messages.error(
                request,
                "Only PDF, DOCX, and TXT files are supported."
            )

            return redirect("home")

        try:

            resume_text = extract_text_from_file(
                uploaded_file
            )

        except Exception:

            messages.error(
                request,
                "Unable to read the uploaded resume."
            )

            return redirect("home")

        if not resume_text.strip():

            messages.error(
                request,
                "No readable text was found in the resume."
            )

            return redirect("home")

        detected_skills = detect_skills(
            resume_text
        )

        score = calculate_resume_score(
            resume_text
        )

        category = detect_resume_category(
            detected_skills
        )

        job_skills = find_job_skills(
            category
        )

        matched_skills, missing_skills, match_percentage = match_job(
            detected_skills,
            job_skills
        )

        suggestions = generate_suggestions(
            resume_text,
            detected_skills,
            missing_skills
        )

        analysis = ResumeAnalysis.objects.create(

            user=request.user,

            resume_name=uploaded_file.name,

            resume_text=resume_text,

            job_description=job_description,

            score=score,

            category=category,

            detected_skills=", ".join(
                detected_skills
            ),

            job_skills=", ".join(
                job_skills
            ),

            matched_skills=", ".join(
                matched_skills
            ),

            missing_skills=", ".join(
                missing_skills
            ),

            match_percentage=match_percentage,
        )

        return render(
            request,
            "results.html",
            {
                "analysis": analysis,
                "detected_skills": detected_skills,
                "job_skills": job_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "match_percentage": match_percentage,
                "suggestions": suggestions,
            }
        )

    return render(
        request,
        "home.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    analyses = ResumeAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_resumes = analyses.count()

    average_score = analyses.aggregate(
        Avg("score")
    )["score__avg"]

    if average_score is None:

        average_score = 0

    else:

        average_score = round(
            average_score
        )

    average_match = analyses.aggregate(
        Avg("match_percentage")
    )["match_percentage__avg"]

    if average_match is None:

        average_match = 0

    else:

        average_match = round(
            average_match
        )

    return render(
        request,
        "dashboard.html",
        {
            "analyses": analyses,

            "recent_analyses": analyses[:5],

            "total_resumes": total_resumes,

            "total_analyses": total_resumes,

            "average_score": average_score,

            "average_match": average_match,

            "average_job_match": average_match,
        }
    )


# ============================================================
# RESUME HISTORY
# ============================================================

@login_required
def resume_history(request):

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    analyses = ResumeAnalysis.objects.filter(
        user=request.user
    ).order_by("-created_at")

    if search_query:

        analyses = analyses.filter(
            resume_name__icontains=search_query
        )

    return render(
        request,
        "history.html",
        {
            "analyses": analyses,
            "search_query": search_query,
        }
    )


# ============================================================
# RESUME DETAILS
# ============================================================

@login_required
def resume_details(request, id):

    analysis = get_object_or_404(
        ResumeAnalysis,
        pk=id,
        user=request.user
    )

    detected_skills = [
        skill.strip()
        for skill in analysis.detected_skills.split(",")
        if skill.strip()
    ]

    job_skills = [
        skill.strip()
        for skill in analysis.job_skills.split(",")
        if skill.strip()
    ]

    matched_skills = [
        skill.strip()
        for skill in analysis.matched_skills.split(",")
        if skill.strip()
    ]

    missing_skills = [
        skill.strip()
        for skill in analysis.missing_skills.split(",")
        if skill.strip()
    ]

    return render(
        request,
        "details.html",
        {
            "analysis": analysis,

            "detected_skills": detected_skills,

            "job_skills": job_skills,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,
        }
    )


# ============================================================
# DELETE HISTORY
# ============================================================

@login_required
def delete_history(request, id):

    analysis = get_object_or_404(
        ResumeAnalysis,
        pk=id,
        user=request.user
    )

    if request.method == "POST":

        analysis.delete()

        messages.success(
            request,
            "Resume analysis deleted successfully."
        )

        return redirect(
            "history"
        )

    return render(
        request,
        "confirm_delete.html",
        {
            "analysis": analysis
        }
    )


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile(request):

    user = request.user

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip()

        user.email = email

        user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect(
            "profile"
        )

    return render(
        request,
        "profile.html",
        {
            "user": user
        }
    )


# ============================================================
# PDF REPORT
# ============================================================

@login_required
def download_report(request, id):

    analysis = get_object_or_404(
        ResumeAnalysis,
        pk=id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="resume_report_{analysis.id}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    y = height - 50

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        50,
        y,
        "AI Resume Analyzer Report"
    )

    y -= 35

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        50,
        y,
        f"Resume: {analysis.resume_name}"
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Category: {analysis.category}"
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Resume Score: {analysis.score}/100"
    )

    y -= 20

    pdf.drawString(
        50,
        y,
        f"Job Match: {analysis.match_percentage}%"
    )

    y -= 30

    # Detected skills

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        y,
        "Detected Skills"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        10
    )

    detected_text = analysis.detected_skills or "None"

    lines = simpleSplit(
        detected_text,
        "Helvetica",
        10,
        width - 100
    )

    for line in lines:

        pdf.drawString(
            50,
            y,
            line
        )

        y -= 15

    y -= 10

    # Matched skills

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        y,
        "Matched Skills"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        10
    )

    matched_text = analysis.matched_skills or "None"

    lines = simpleSplit(
        matched_text,
        "Helvetica",
        10,
        width - 100
    )

    for line in lines:

        pdf.drawString(
            50,
            y,
            line
        )

        y -= 15

    y -= 10

    # Missing skills

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        y,
        "Missing Skills"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        10
    )

    missing_text = analysis.missing_skills or "None"

    lines = simpleSplit(
        missing_text,
        "Helvetica",
        10,
        width - 100
    )

    for line in lines:

        pdf.drawString(
            50,
            y,
            line
        )

        y -= 15

        if y < 60:

            pdf.showPage()

            y = height - 50

            pdf.setFont(
                "Helvetica",
                10
            )

    pdf.save()

    return response


# ============================================================
# REGISTER
# ============================================================

def register(request):

    if request.user.is_authenticated:

        return redirect(
            "dashboard"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return redirect(
                "register"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                "register"
            )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect(
                "register"
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Registration successful."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

def user_login(request):

    if request.user.is_authenticated:

        return redirect(
            "dashboard"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

def user_logout(request):

    logout(
        request
    )

    return redirect(
        "login"
    )