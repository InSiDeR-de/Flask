from flask import Flask, flash, render_template, g, redirect, url_for, request
import secrets
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
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
            return render_template('add_task.html', error=flash(f'Nie można dodać zadania o nazwie krótszej niż 4 znaki'))
        db = get_db()
        existingtask = db.execute("SELECT id FROM tasks WHERE title LIKE ?", [title]).fetchone()
        if existingtask:
            return render_template('add_task.html', error=flash(f'Zadanie o tej samej nazwie już istnieje'))
        db.execute("INSERT INTO tasks (title, done) VALUES (?,?)", [title,0])
        db.commit()
        return redirect(url_for('list'))
    return render_template('add_task.html')

@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id, is_task_view=False):
    db = get_db()
    task = db.execute("SELECT id, done FROM tasks WHERE id = ?", [task_id]).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        db.execute("UPDATE tasks SET done = ? WHERE id = ?", [new_status, task_id])
        db.commit()
        flash(f'Zadanie o ID {task_id} zostało oznaczone jako {"zrobione" if new_status else "niezrobione"}', 'success')
        is_task_view = request.form.get('is_task_view') == 'true'
        if is_task_view:
            return redirect(url_for('task', task_id=task_id))
    return redirect(url_for('list'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", [task_id])
    db.commit()
    flash=(f'Zadanie o ID {task_id} zostało usunięte.', 'success')
    return redirect(url_for('list'))

@app.route('/tasks/<int:task_id>')
def task(task_id):
    db = get_db()
    task = db.execute("SELECT id, title, done, created_at FROM tasks WHERE id = ?", [task_id]).fetchone()
    if task is None:
        return redirect(url_for('list'))
    return render_template('task.html', task=task)

@app.route('/tasks/<int:task_id>/change_tittle', methods=['POST'])
def change_title(task_id):
    db = get_db()
    new_title = request.form.get('title').strip()
    if len(new_title) < 4:
        flash(f'Nowa nazwa zadania musi mieć co najmniej 4 znaki.', 'error')
    else:
        db.execute("UPDATE tasks SET title = ? WHERE id = ?", [new_title, task_id])
        db.commit()
        flash(f'Zmieniono nazwę zadania na: {new_title}', 'success')
    return redirect(url_for('task', task_id=task_id))

if __name__ == '__main__':
    app.run(debug=True)
