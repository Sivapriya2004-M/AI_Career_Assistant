from flask import Flask, render_template, request
import os
import PyPDF2
from docx import Document

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# -------------------- FILE EXTRACTORS --------------------

def extract_pdf(path):
    text = ""
    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    return text


def extract_docx(path):
    doc = Document(path)
    text = ""

    for para in doc.paragraphs:
        text += para.text + " "

    return text


def extract_txt(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def extract_text(path):
    if path.endswith(".pdf"):
        return extract_pdf(path)
    elif path.endswith(".docx"):
        return extract_docx(path)
    elif path.endswith(".txt"):
        return extract_txt(path)
    return ""


# -------------------- SKILLS DATABASE --------------------

skills_db = [
    "Python", "Java", "SQL", "HTML", "CSS",
    "JavaScript", "Flask", "Django", "Git",
    "AWS", "Docker", "Machine Learning"
]


# -------------------- ROUTES --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    resume = request.files["resume"]

    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
    resume.save(resume_path)

    resume_text = extract_text(resume_path)

    jd_text = request.form.get("jd_text")
    jd_file = request.files.get("jd_file")

    # If JD uploaded as file
    if jd_file and jd_file.filename != "":
        jd_path = os.path.join(app.config["UPLOAD_FOLDER"], jd_file.filename)
        jd_file.save(jd_path)
        jd_text = extract_text(jd_path)

    # -------------------- SKILL MATCHING --------------------

    found_skills = []
    for skill in skills_db:
        if skill.lower() in resume_text.lower():
            found_skills.append(skill)

    jd_skills = []
    if jd_text:
        for skill in skills_db:
            if skill.lower() in jd_text.lower():
                jd_skills.append(skill)

    matched_skills = []
    for skill in found_skills:
        if skill in jd_skills:
            matched_skills.append(skill)

    missing_skills = []
    for skill in jd_skills:
        if skill not in found_skills:
            missing_skills.append(skill)

    # -------------------- MATCH PERCENT --------------------

    if len(jd_skills) > 0:
        match_percent = round(len(matched_skills) / len(jd_skills) * 100, 2)
    else:
        match_percent = 0

    # -------------------- ATS SCORE --------------------

    score = 0
    score += min(len(found_skills) * 5, 50)

    if "project" in resume_text.lower():
        score += 20
    if "internship" in resume_text.lower():
        score += 15
    if "certification" in resume_text.lower():
        score += 15

    score = min(score, 100)

    # -------------------- JOBS --------------------

    recommended_jobs = []

    if "Python" in found_skills:
        recommended_jobs.append("Python Developer")
    if "SQL" in found_skills:
        recommended_jobs.append("Data Analyst")
    if "Machine Learning" in found_skills:
        recommended_jobs.append("AI Engineer")

    # -------------------- ROADMAP --------------------

    roadmap = []
    for i, skill in enumerate(missing_skills):
        roadmap.append(f"Week {i+1} → Learn {skill}")

    # -------------------- INTERVIEW QUESTIONS --------------------

    interview_questions = """
Technical Questions:
1. What is Python?
2. Explain OOP concepts.
3. What is SQL JOIN?
4. What is Flask?
5. What is Machine Learning?

HR Questions:
1. Tell me about yourself.
2. Why should we hire you?
3. What are your strengths?
4. Describe a challenging project.
5. Where do you see yourself in 5 years?
"""

    return render_template(
        "result.html",
        score=score,
        skills=found_skills,
        match_percent=match_percent,
        missing_skills=missing_skills,
        interview_questions=interview_questions,
        recommended_jobs=recommended_jobs,
        roadmap=roadmap
    )


# -------------------- RUN APP --------------------

if __name__ == "__main__":
    app.run(debug=True)
