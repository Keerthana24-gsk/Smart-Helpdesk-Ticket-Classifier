from flask import Flask, render_template, request
import sqlite3
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


def init_db():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue TEXT,
            category TEXT,
            solution TEXT
        )
    """)

    conn.commit()
    conn.close()


def classify_issue(issue):
    doc = nlp(issue.lower())

    tokens = [token.text for token in doc]

    login_words = {"login", "password", "signin", "account"}
    network_words = {"network", "internet", "wifi", "connection"}
    software_words = {"crash", "error", "application", "software", "bug"}

    if any(word in tokens for word in login_words):
        return (
            "Login",
            "Reset password and verify username."
        )

    elif any(word in tokens for word in network_words):
        return (
            "Network",
            "Check internet connection and restart router."
        )

    elif any(word in tokens for word in software_words):
        return (
            "Software",
            "Restart application and check updates."
        )

    else:
        return (
            "General",
            "Please contact support for detailed diagnosis."
        )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    issue = request.form["issue"]

    category, solution = classify_issue(issue)

    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO tickets (issue, category, solution) VALUES (?, ?, ?)",
        (issue, category, solution)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        issue=issue,
        category=category,
        solution=solution
    )


@app.route("/history")
def history():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()

    c.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = c.fetchall()

    conn.close()

    return render_template("history.html", tickets=tickets)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)