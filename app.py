from flask import Flask, render_template, request, jsonify, session
import re

app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# 🧠 SKILL EXTRACTION
# -----------------------------
def extract_skills(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {"and", "the", "with", "for", "this", "that"}
    skills = [w for w in words if w not in stopwords]
    return list(set(skills))[:5]


# -----------------------------
# 💬 QUESTION GENERATION
# -----------------------------
def generate_questions(skills):
    return [f"Explain your experience with {s} with an example." for s in skills]


# -----------------------------
# 📊 SCORING
# -----------------------------
def score_answer(ans):
    ans = ans.lower()
    score = 0

    if "example" in ans: score += 3
    if "project" in ans: score += 3
    if "used" in ans or "implemented" in ans: score += 2
    if len(ans.split()) > 15: score += 2

    return min(score, 10)


# -----------------------------
# 🎯 ADJACENT SKILLS
# -----------------------------
ADJACENT = {
    "python": ["django", "flask"],
    "flask": ["docker", "api"],
    "sql": ["database", "optimization"],
    "marketing": ["seo", "analytics"]
}


def get_adjacent(skills):
    result = []
    for s in skills:
        if s in ADJACENT:
            result.extend(ADJACENT[s])
    return list(set(result))


# -----------------------------
# 📚 LEARNING PLAN
# -----------------------------
def learning_plan(skills):
    plan = []
    for s in skills:
        plan.append(f"Learn {s} basics (5 days) + build mini project")
    return plan


# -----------------------------
# 🏠 HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# 🚀 START ANALYSIS
# -----------------------------
@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()

    jd = data.get("jd", "")
    resume = data.get("resume", "")

    skills = extract_skills(jd + resume)
    questions = generate_questions(skills)

    session["skills"] = skills
    session["questions"] = questions
    session["answers"] = []
    session["index"] = 0

    return jsonify({"question": questions[0]})


# -----------------------------
# 💬 NEXT QUESTION
# -----------------------------
@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    ans = data.get("answer", "")

    session["answers"].append(ans)
    session["index"] += 1

    if session["index"] < len(session["questions"]):
        return jsonify({
            "question": session["questions"][session["index"]]
        })
    else:
        return jsonify({"done": True})


# -----------------------------
# 📊 RESULT
# -----------------------------
@app.route("/result")
def result():
    skills = session.get("skills", [])
    answers = session.get("answers", [])

    scores = [score_answer(a) for a in answers]

    strong = []
    weak = []

    for s, sc in zip(skills, scores):
        if sc >= 7:
            strong.append((s, sc))
        else:
            weak.append((s, sc))

    adjacent = get_adjacent([s for s, _ in weak])
    plan = learning_plan([s for s, _ in weak] + adjacent)

    return render_template("result.html",
                           strong=strong,
                           weak=weak,
                           plan=plan)


# -----------------------------
# 🚀 RUN
# -----------------------------
if __name__ == "__main__":
import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)