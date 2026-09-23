from flask import redirect, session
from functools import wraps
from cs50 import SQL

db = SQL("sqlite:///project.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def sqlQuery(user_id):
    credit_totals = {semester: 0 for semester in range(1, 9)}
    credits = db.execute("SELECT semester, SUM(credits) AS credits FROM courses JOIN userinfo ON userinfo.code = courses.code WHERE userinfo.user_id = ? GROUP BY semester ORDER BY semester", user_id)
    for row in credits:
        credit_totals[row["semester"]] = row["credits"]
    completed_courses = db.execute("SELECT userinfo.id, courses.code, name, semester,credits FROM courses JOIN userinfo ON courses.code = userinfo.code WHERE user_id = ?", user_id)
    return completed_courses, credit_totals
