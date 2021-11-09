import sqlite3 as sl

db = sl.connect('database.db')


def setup_db():
    with db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            file TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)


def has_been_crawled(link) -> bool:
    exists = db.execute("""SELECT * FROM links WHERE link = ?""", [link]).fetchone()
    return exists is not None


def save_has_been_crawled(link):
    cur = db.cursor()
    cur.execute("""INSERT INTO links (link) VALUES (?)""", [link])
    db.commit()


def is_to_be_downloaded(file) -> bool:
    exists = db.execute("""SELECT * FROM downloads WHERE file = ? AND status = 'pending'""", [file]).fetchone()
    return exists is not None


def has_been_downloaded(file) -> bool:
    exists = db.execute("""SELECT * FROM downloads WHERE file = ? AND status = 'done'""", [file]).fetchone()
    return exists is not None


def get_files_to_be_downloaded() -> list:
    return db.execute("""SELECT file FROM downloads WHERE status = 'pending'""").fetchall()


def save_to_be_downloaded(file):
    cur = db.cursor()
    cur.execute("""INSERT INTO downloads (file) VALUES (?)""", [file])
    db.commit()


def save_has_been_downloaded(file):
    cur = db.cursor()
    cur.execute("""UPDATE downloads SET status = 'done' WHERE file = ?""", [file])
    db.commit()
