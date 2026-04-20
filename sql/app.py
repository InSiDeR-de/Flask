from flask import Flask, render_template, g, redirect, url_for, request
import sqlite3

app = Flask(__name__)
DATABASE = 'todo.db'
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
"""

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()    

def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Baza danych ToDo została zainicjalizowana.')

@app.cli.command('seed-db')
def seed_db_command():
    db = get_db()
    rows = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if rows == 0:
        db.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", [
            ('Iść po mleko', 0),
            ('Wygrać w kasynie', 0),
            ('Otworzyć cieśninę', 1),
        ])
        db.commit()
        print('Dodano przykładowe zadania do bazy danych.')
    else:
        print('Baza danych nie jest pusta, pomijam seed')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
        db = get_db()
        db.execute("SELECT 1").fetchone()
        return render_template('ping.html')

@app.route('/list')
def list():
    db = get_db()
    tasks = db.execute("SELECT id, title, done, created_at FROM tasks ORDER BY created_at DESC").fetchall()
    return render_template('list.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        if len(title) < 4:
            return render_template('add_task.html', error=f'Nie można dodać zadania o nazwie krótszej niż 4 znaki')
        db = get_db()
        existingtask = db.execute("SELECT id FROM tasks WHERE title LIKE ?", [title]).fetchone()
        if existingtask:
            return render_template('add_task.html', error=f'Zadanie o tej samej nazwie już istnieje')
        db.execute("INSERT INTO tasks (title, done) VALUES (?,?)", [title,0])
        db.commit()
        return redirect(url_for('list'))
    return render_template('add_task.html')


if __name__ == '__main__':
    app.run(debug=True)