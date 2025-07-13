import sqlite3
import bcrypt
import pandas as pd


def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    firstname TEXT,
                    lastname TEXT,
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    token TEXT
                )''')
    conn.commit()
    conn.close()

def create_flashcard_tables():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Flashcards table
    c.execute('''CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    word TEXT,
                    meaning TEXT,
                    example TEXT,
                    ease REAL DEFAULT 2.5,
                    repetitions INTEGER DEFAULT 0,
                    interval INTEGER DEFAULT 0,
                    next_review TEXT
                )''')
    conn.commit()
    conn.close()


def init_quiz_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            score INTEGER,
            total_questions INTEGER,
            quiz_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_learning_history_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            lesson_name TEXT,
            quiz_score REAL,
            total_questions REAL,
            completion_time REAL,
            dropped_out INTEGER DEFAULT 0,
            date_completed TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_token(username, token):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET token=? WHERE username=?", (token, username))
    conn.commit()
    conn.close()


def get_username_by_token(token):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE token=?", (token,))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None


def register_user(username, password, firstname, lastname):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (firstname, lastname, username, password_hash) VALUES (?, ?, ?, ?)", (firstname, lastname, username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user[0]):
        return True
    return False




def save_flashcards(username, cards):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    for card in cards:
        c.execute("""
            INSERT INTO flashcards (username, word, meaning, example, ease, repetitions, interval, next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            card["word"],
            card["meaning"],
            card["example"],
            2.5,  # ease
            0,  # reps
            0,  # interval
            None  # next_review
        ))
    conn.commit()
    conn.close()


def get_due_flashcards(username):
    from datetime import datetime
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("""
        SELECT id, word, meaning, example, ease, repetitions, interval
        FROM flashcards
        WHERE username=? AND (next_review IS NULL OR next_review <= ?)
    """, (username, today))

    return c.fetchall()


def update_card_schedule(card_id, ease, repetitions, interval, next_review):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        UPDATE flashcards
        SET ease=?, repetitions=?, interval=?, next_review=?
        WHERE id=?
    """, (ease, repetitions, interval, next_review, card_id))
    conn.commit()
    conn.close()




def save_learning_progress(username, lesson, score, total_questions,  time_spent):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO learning_history (username, lesson_name, quiz_score, total_questions, completion_time, dropped_out)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, lesson, score, total_questions, time_spent, 0))
        conn.commit()
        return True  # Return True on success
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")  # Print error to console/log
        return False  # Return False on failure
    except Exception as e:
        print(f"Unexpected error occurred: {e}")  # Catch other unexpected errors
        return False
    finally:
        if conn:
            conn.close()  # Ensure connection is closed even if error occurs

def get_user_learning_features(username):
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query(
        "SELECT * FROM learning_history WHERE username = ?",
        conn,
        params=[username]  # Note: params should be a list, not a tuple
    )
    conn.close()

    if df.empty:
        return [0, 0, 0]

    return [
        float(df['completion_time'].mean()) if 'completion_time' in df else 0,
        float(df['quiz_score'].mean()) if 'quiz_score' in df else 0,
        len(df)
    ]


def fetch_due_flashcards(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM flashcards WHERE user=? AND (next_review IS NULL OR next_review <= ?)",
              (username, today))
    rows = c.fetchall()
    conn.close()
    return rows


def update_flashcard(card_id, ease, repetitions, interval, next_review):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE flashcards SET ease=?, repetitions=?, interval=?, next_review=? WHERE id=?",
              (ease, repetitions, interval, next_review, card_id))
    conn.commit()
    conn.close()





def save_quiz_score(username, score, total, quiz_type):
    from datetime import datetime
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO quiz_results (username, timestamp, score, total_questions, quiz_type)
        VALUES (?, ?, ?, ?, ?)
    """, (username, datetime.now().isoformat(), score, total, quiz_type))
    conn.commit()
    conn.close()


def get_user_quiz_scores(username, limit=10):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, score, total_questions, quiz_type FROM quiz_results
        WHERE username=?
        ORDER BY timestamp DESC LIMIT ?
    """, (username, limit))
    scores = c.fetchall()
    conn.close()
    return scores
