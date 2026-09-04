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
        return redirect('/round2')

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


# ===== LEVEL 2: SQL INJECTION SNAKE =====
@app.route('/level2')
def level2_intro():
    session.pop('level2_r1', None)
    session.pop('level2_r2', None)
    return render_template('level2_intro.html', score=session.get('score', 0))


@app.route('/level2/round1')
def level2_round1():
    return render_template('level2_round1.html', score=session.get('score', 0))


@app.route('/check-level2-round1', methods=['POST'])
def check_level2_round1():
    choice = request.form.get('query', '')

    if "' OR '1'='1" in choice or '" OR "1"="1' in choice:
        session['level2_r1'] = True
        session['score'] = session.get('score', 0) + 150
        return redirect('/level2/round2')

    return render_template(
        'level2_round1.html',
        score=session.get('score', 0),
        error="Snake slipped away! That query didn't inject. Look for OR '1'='1.",
    )


@app.route('/level2/round2')
def level2_round2():
    if not session.get('level2_r1'):
        return redirect('/level2/round1')
    return render_template('level2_round2.html', score=session.get('score', 0))


@app.route('/check-level2-round2', methods=['POST'])
def check_level2_round2():
    patch = request.form.get('patch', '')

    if '?' in patch or 'parameter' in patch.lower() or 'prepared' in patch.lower():
        session['level2_r2'] = True
        session['score'] = session.get('score', 0) + 200
        return redirect('/level2/boss')

    return render_template(
        'level2_round2.html',
        score=session.get('score', 0),
        error='Still vulnerable! Use parameterized queries (?).',
    )


@app.route('/level2/boss')
def level2_boss():
    if not session.get('level2_r2'):
        return redirect('/level2/round1')
    return render_template('level2_boss.html', score=session.get('score', 0))

if __name__ == '__main__':
    app.run(debug=True)
