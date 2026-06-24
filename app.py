from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

paragraphs = [
"Technology is changing the world very fast. People are learning new digital skills every day. Coding is becoming an important skill for students. It helps in logical thinking and problem solving.",

"Typing speed is a useful skill for students and professionals. Regular practice improves accuracy and speed. Many jobs require good typing skills. It saves time and increases productivity.",

"Python is a simple and powerful programming language. It is used in web development, AI, and data science. Beginners can easily learn Python. It has simple syntax and large community support.",

"Artificial intelligence is changing modern life. It is used in healthcare, education, and gaming. AI helps machines think and learn like humans. It makes tasks faster and smarter.",

"The internet connects people all over the world. We can communicate instantly using social media. It provides information on every topic. But we should use it safely and wisely.",

"Good habits lead to a successful life. Waking up early improves productivity. Reading books increases knowledge. Discipline is the key to success.",

"Education is the foundation of a strong society. It helps people grow and develop skills. Teachers play an important role in learning. Education opens many opportunities.",

"Web development includes frontend and backend. HTML, CSS, and JavaScript are used for frontend. Backend handles data and server logic. Both are important for websites.",

"Mobile phones are an important part of life. They help in communication and entertainment. But excessive use can be harmful. Balance is important for healthy living.",

"Cyber security protects data from hackers. Strong passwords are very important. We should avoid unknown links and emails. Safety on the internet is necessary.",

"Practice makes a person perfect. The more you practice, the better you become. Consistency is very important. Never give up on learning.",

"Time management is very important for success. Planning your day increases productivity. Avoid wasting time on useless activities. Focus on your goals.",

"Reading books improves knowledge and imagination. It also reduces stress. Good books help in personality development. Everyone should read daily.",

"Sports keep the body healthy and strong. They improve teamwork and discipline. Playing games is good for mental health. Regular exercise is necessary.",

"Hard work is the key to success. There is no shortcut to success. Consistency and dedication are important. Never stop working towards your goals.",

"The sun gives energy to all living beings. Plants use sunlight for photosynthesis. It is the main source of life on Earth. Without it, life cannot exist.",

"Water is essential for life. We should drink clean water daily. It keeps the body healthy. Saving water is very important.",

"Honesty is the best policy. It builds trust between people. Honest people are respected in society. Always speak the truth.",

"Trees are very important for the environment. They give us oxygen and shade. Cutting trees harms nature. We should plant more trees.",

"Science helps us understand the world. It explains natural phenomena. New inventions make life easier. Science improves human life.",

"Music is a great source of relaxation. It reduces stress and improves mood. People enjoy different types of music. It is part of every culture.",

"Traveling helps us learn new things. We explore new places and cultures. It gives us unforgettable experiences. Traveling broadens the mind.",

"Teamwork is important in every field. It improves efficiency and results. Working together solves problems faster. Unity leads to success.",

"Confidence helps in achieving goals. It improves personality and communication. Believe in yourself always. Confidence leads to success.",

"Discipline is the foundation of success. It helps in achieving goals on time. Without discipline life becomes chaotic. It builds strong character.",

"Learning new skills is important in life. It helps in career growth. Continuous learning keeps you updated. Knowledge is power.",

"Positive thinking improves mental health. It helps in solving problems easily. Always stay hopeful in life. Positivity brings happiness.",

"Technology is evolving every day. New inventions are making life easier. Automation is increasing in industries. Future will be more digital.",

"Programming helps in building software. It requires logic and creativity. Developers solve real world problems. It is a high demand skill.",

"Success comes with patience and hard work. Never stop learning and growing. Every failure teaches a lesson. Keep moving forward in life."
]

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

#------------------SAVE SCORE------------------------
init_db()
@app.route("/save-score", methods=["POST"])
def save_score():

    if "user" not in session:
        return "Login Required"

    data = request.get_json()
    wpm = float(data["wpm"])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT best_wpm FROM users WHERE username=?",
        (session["user"],)
    )

    current = cursor.fetchone()[0]

    if wpm > current:
        cursor.execute(
            "UPDATE users SET best_wpm=? WHERE username=?",
            (wpm, session["user"])
        )
        conn.commit()

    conn.close()

    return "OK"
#--------------------------LEADERBOARD-----------------------
@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, best_wpm
        FROM users
        ORDER BY best_wpm DESC
        LIMIT 20
    """)

    scores = cursor.fetchall()
    conn.close()

    return render_template("leaderboard.html", scores=scores)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                      (username, hashed_password))
            conn.commit()
        except:
            return "User already exists!"

        conn.close()
        return redirect("/login")

    return render_template("register.html")
    print("Registered:", username, password)

# --------------------change paragraph-------------------
@app.route("/change-paragraph")
def change_paragraph():

    current = session.get("current_paragraph")

    new_para = random.choice(paragraphs)

    while new_para == current:
        new_para = random.choice(paragraphs)

    session["current_paragraph"] = new_para

    return redirect("/")

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (session["user"], old_password)
        )

        user = c.fetchone()

        if not user:
            conn.close()
            return "Old password is incorrect!"

        c.execute(
            "UPDATE users SET password=? WHERE username=?",
            (new_password, session["user"])
        )

        conn.commit()
        conn.close()

        return "Password changed successfully!"

    return render_template("change_password.html")

# -------------------dashboard-----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute( "SELECT * FROM users WHERE username=?",
        (username,)
)

        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "current_paragraph" not in session:
        session["current_paragraph"] = random.choice(paragraphs)

    user = session.get("user")

    return render_template(
        "index.html",
        paragraph=session["current_paragraph"],
        user=user
    )
import os
from flask import send_from_directory

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "sitemap.xml")

@app.route("/robots.txt")
def robots():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "robots.txt") 

if __name__ == "__main__":
    app.run(debug=True)