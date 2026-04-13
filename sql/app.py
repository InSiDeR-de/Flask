from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = 'todo.db'

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)