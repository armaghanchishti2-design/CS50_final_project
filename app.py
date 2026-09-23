import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, sqlQuery
# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def courses():
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM courses")
    return render_template("courses.html", rows=rows)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return render_template("apology.html", apology="No field should be empty!")
        if password != confirmation:
            return render_template("apology.html", apology="Passwords do not match!")
        row = db.execute("SELECT * FROM people WHERE username = ?", username)
        if len(row) > 0:
            return render_template("apology.html", apology="Username already taken!")
        hash_value = generate_password_hash(password)
        db.execute("INSERT INTO people(username, password) VALUES(?, ?)", username, hash_value)
        row = db.execute("SELECT * FROM people WHERE username = ?", username)
        session["user_id"] = row[0]["id"]
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", apology="Must provide username!")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", apology="Must provide password!")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM people WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return render_template("apology.html", apology="Invalid username and/or password!")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM courses")
    if request.method == "GET":
        completed, credits = sqlQuery(user_id)
        return render_template("planner.html", rows=rows, message="", completed=completed, credits=credits)
    delete_id = request.form.get("delete_row")
    if delete_id != None:
        db.execute("DELETE FROM userinfo WHERE id = ?", delete_id)
        completed, credits = sqlQuery(user_id)
        message = "Course removed!"
    else:
        course_id = request.form.get("course_id")
        semester = request.form.get("semester")
        course_details = db.execute("SELECT code, credits FROM courses WHERE id = ?", course_id)
        prerequisites = db.execute(
            "SELECT prerequisite FROM prerequisites WHERE course = ?", course_details[0]["code"])
        selected_course = db.execute(
            "SELECT * FROM userinfo WHERE user_id = ? AND code = ?", user_id, course_details[0]["code"])
        semester_credits = db.execute(
            "SELECT SUM(credits) AS credits FROM courses JOIN userinfo ON userinfo.code = courses.code WHERE user_id = ? AND semester = ?", user_id, semester)
        if semester_credits[0]["credits"] == None:
            semester_credits[0]["credits"] = 0
        total_credits = int(course_details[0]["credits"]) + int(semester_credits[0]["credits"])
        if total_credits > 18:
            completed, credits = sqlQuery(user_id)
            message = "You cannot exceed 18 credits per semester!"
        elif len(selected_course) == 1:
            completed, credits = sqlQuery(user_id)
            message = "Course already chosen!"
        elif len(prerequisites) == 0:
            db.execute("INSERT INTO userinfo (user_id,semester,code) VALUES (?,?,?)",
                       user_id, semester, course_details[0]["code"])
            completed, credits = sqlQuery(user_id)
            message = "Course added!"
        else:
            user_courses = db.execute(
                "SELECT semester,code FROM userinfo WHERE user_id = ?", user_id)
            found = False
            for course in user_courses:
                for prerequisite in prerequisites:
                    if (course["code"] == prerequisite["prerequisite"]) and course["semester"] <= int(semester):
                        found = True

            if found:
                db.execute("INSERT INTO userinfo (user_id,semester,code) VALUES (?,?,?)",
                           user_id, semester, course_details[0]["code"])
                completed, credits = sqlQuery(user_id)
                message = "Course added!"
            else:
                completed, credits = sqlQuery(user_id)
                message = "Complete the prerequisite in the previous semester first!"

    return render_template("planner.html", rows=rows, message=message, completed=completed, credits=credits)

@app.route("/grades", methods=["GET", "POST"])
@login_required
def grades():
    user_id = session["user_id"]
    grade_points = {
        "A+": 4.3,
        "A": 4.0,
        "A-": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "B-": 2.7,
        "C+": 2.3,
        "C": 2.0,
        "C-": 1.7,
        "D+": 1.3,
        "D": 1.0,
        "D-": 0.7,
        "F": 0.0
    }
    if request.method == "GET":
        gpas = db.execute("SELECT * FROM gpa WHERE user_id = ?", user_id)
        all_gpas = {semester: 0 for semester in range(1, 9)}
        for gpa in gpas:
            all_gpas[gpa["semester"]] = gpa["gpa"]
        completed_courses = db.execute(
            "SELECT userinfo.id, courses.code, name, semester, grade FROM courses JOIN userinfo ON courses.code = userinfo.code WHERE user_id = ?", user_id)
        return render_template("grades.html", completed=completed_courses, gpa=all_gpas)
    total_points = 0
    semester = request.form.get("semester")
    total_course_credits = 0
    courses = db.execute(
        "SELECT userinfo.id, courses.code, name, credits FROM courses JOIN userinfo ON courses.code = userinfo.code WHERE userinfo.user_id = ? AND userinfo.semester = ?", user_id, semester)
    for course in courses:
        grade = request.form.get(f"grade_{course['id']}")
        db.execute("UPDATE userinfo SET grade = ? WHERE user_id = ? AND code = ?",
                   grade, user_id, course['code'])
        points = grade_points[grade]
        total_points = total_points + (points * int(course["credits"]))
        total_course_credits += int(course["credits"])
    try:
        gpa = total_points/total_course_credits
    except ZeroDivisionError:
        gpa = 0
    gpa = round(gpa, 2)
    db.execute("INSERT INTO gpa(semester, gpa, user_id) VALUES(?, ?, ?) ON CONFLICT(semester, user_id) DO UPDATE SET gpa = excluded.gpa", semester, gpa, user_id)
    gpas = db.execute("SELECT * FROM gpa WHERE user_id = ?", user_id)
    all_gpas = {semester: 0 for semester in range(1, 9)}
    for gpa in gpas:
        all_gpas[gpa["semester"]] = gpa["gpa"]
    completed_courses = db.execute(
        "SELECT userinfo.id, courses.code, name, semester, grade FROM courses JOIN userinfo ON courses.code = userinfo.code WHERE user_id = ?", user_id)
    return render_template("grades.html", completed=completed_courses, gpa=all_gpas)

@app.route("/progress")
@login_required
def progress():
    user_id = session["user_id"]
    grade_points = {
        "A+": 4.3,
        "A": 4.0,
        "A-": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "B-": 2.7,
        "C+": 2.3,
        "C": 2.0,
        "C-": 1.7,
        "D+": 1.3,
        "D": 1.0,
        "D-": 0.7,
        "F": 0.0
    }
    total_points = 0
    total_course_credits = 0
    courses = db.execute(
        "SELECT credits, grade FROM courses JOIN userinfo ON courses.code = userinfo.code WHERE userinfo.user_id = ?", user_id)
    for course in courses:
        points = grade_points[course["grade"]]
        total_points = total_points + (points * int(course["credits"]))
        total_course_credits += int(course["credits"])
    if total_course_credits > 0:
        if total_course_credits > 120:
            total_course_credits = 120
        cgpa = total_points/total_course_credits
    else:
        cgpa = 0.0
    cgpa = round(cgpa, 2)
    percentage = (total_course_credits/120)*100
    percentage = round(percentage)
    name = db.execute("SELECT username FROM people WHERE id = ?", user_id)
    username = name[0]["username"].upper()
    highest = db.execute("SELECT MAX(gpa) AS Max FROM gpa WHERE user_id = ?", user_id)
    remaining = 120-total_course_credits
    return render_template("progress.html", cgpa=cgpa, percentage=percentage, total=total_course_credits, name=username, highest=highest[0]["Max"], remaining=remaining)
