from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create database if it doesn't exist
if not os.path.exists('library.db'):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, category TEXT)''')
    
    # Insert 10 sample books
    books = [
        ("The Alchemist", "Paulo Coelho", "Fiction"),
        ("Wings of Fire", "A.P.J. Abdul Kalam", "Biography"),
        ("Clean Code", "Robert C. Martin", "Programming"),
        ("1984", "George Orwell", "Dystopian"),
        ("To Kill a Mockingbird", "Harper Lee", "Classic"),
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance"),
        ("The Power of Habit", "Charles Duhigg", "Self-help"),
        ("Atomic Habits", "James Clear", "Self-help"),
        ("The Pragmatic Programmer", "Andrew Hunt", "Programming"),
        ("The Psychology of Money", "Morgan Housel", "Finance")
    ]
    c.executemany("INSERT INTO books (title, author, category) VALUES (?, ?, ?)", books)
    conn.commit()
    conn.close()

# Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('books'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        conn = sqlite3.connect('library.db')
        conn.execute("INSERT INTO books (title, author, category) VALUES (?, ?, ?)", (title, author, category))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/books')
def books():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return render_template('books.html', books=books, username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
