import os
import sqlite3

from flask import Flask, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-later')
DATABASE = os.path.join(app.root_path, 'patchquest.db')


def init_db():
    """Create the local leaderboard store on the first run."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            'CREATE TABLE IF NOT EXISTS scores '
            '(id INTEGER PRIMARY KEY, name TEXT NOT NULL, score INTEGER NOT NULL)'
        )


init_db()

@app.route('/')
def home():
    session['score'] = 0
    return render_template('index.html')

@app.route('/round1')
def round1():
    passwords = ["admin123", "P@ssw0rd!2026", "mycvsite", "12345678"]
    return render_template('round1.html', passwords=passwords, score=session.get('score', 0))

@app.route('/check-round1', methods=['POST'])
def check_round1():
    pick = request.form.get('password')
    weak_passwords = ["admin123", "12345678"]

    if pick in weak_passwords:
        session['score'] = session.get('score', 0) + 50
        return render_template(
            'round1.html',
            passwords=["admin123", "P@ssw0rd!2026", "mycvsite", "12345678"],
            score=session['score'],
            result='correct',
            picked=pick,
        )

    return render_template(
        'round1.html',
        passwords=["admin123", "P@ssw0rd!2026", "mycvsite", "12345678"],
        score=session.get('score', 0),
        result='wrong',
        picked=pick,
    )

@app.route('/round2')
def round2():
    return render_template('round2.html', hp=100, score=session.get('score', 0))

@app.route('/round3')
def round3():
    return render_template('round3.html', score=session.get('score', 0))

@app.route('/check-round3', methods=['POST'])
def check_round3():
    answer = request.form.get('answer')

    if answer == 'correct':
        session['score'] = session.get('score', 0) + 100
        return redirect('/win')

    return render_template('round3.html', score=session.get('score', 0), wrong_answer=True)


@app.route('/win')
def win_page():
    return render_template('win.html', score=session.get('score', 0))


@app.route('/save-score', methods=['POST'])
def save_score():
    name = request.form.get('name', '').strip()[:20] or 'Anonymous'
    score = session.get('score', 0)

    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            'INSERT INTO scores (name, score) VALUES (?, ?)', (name, score)
        )

    return redirect('/leaderboard')


@app.route('/leaderboard')
def leaderboard():
    with sqlite3.connect(DATABASE) as connection:
        top = connection.execute(
            'SELECT name, score FROM scores ORDER BY score DESC, id ASC LIMIT 10'
        ).fetchall()

    return render_template('leaderboard.html', top=top)

if __name__ == '__main__':
    app.run(debug=True)
