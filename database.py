import sqlite3 as sl
import json

from dtos import LotteryResults

db = sl.connect('database.db')


def setup_db():
    with db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                link TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
        db.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                file TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
        db.execute("""
            CREATE TABLE IF NOT EXISTS processed (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                result TEXT DEFAULT 'ok',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
        db.execute("""
            CREATE TABLE IF NOT EXISTS lotteries (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                lottery_date TEXT NOT NULL,
                lottery_number TEXT NOT NULL,
                district TEXT NOT NULL,
                shift TEXT NOT NULL,
                numbers TEXT NOT NULL,
                loser_bets TEXT NOT NULL, 
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")


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


def has_been_processed(file) -> bool:
    exists = db.execute("""SELECT * FROM processed WHERE path = ?""", [file]).fetchone()
    return exists is not None


def save_has_been_processed(file, result):
    cur = db.cursor()
    cur.execute("""INSERT INTO processed (path, result) VALUES (?, ?)""", [file, result])
    db.commit()


def save_lottery_results(results: LotteryResults):
    cur = db.cursor()
    cur.execute("""
        INSERT INTO lotteries (lottery_date, lottery_number, district, shift, numbers, loser_bets) 
        VALUES (?, ?, ?, ?, ?, ?)""",
        [results.date, results.lottery_number, results.district, results.shift,  json.dumps(results.numbers), results.losers])
    db.commit()
