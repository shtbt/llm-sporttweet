import sqlite3
import os

DB_PATH = "content_creator.db"
# === Setup Tables ===
with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT UNIQUE,
        published_at TEXT,
        content TEXT,
        score INTEGER,
        reason TEXT,
        proximity INTEGER DEFAULT -1,
        freshness INTEGER DEFAULT -1,
        impact INTEGER DEFAULT -1,
        engagement INTEGER DEFAULT -1,
        uniqueness INTEGER DEFAULT -1,
        virality INTEGER DEFAULT -1,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        posted INTEGER DEFAULT 0
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER,
        caption TEXT,
        tweet TEXT,
        reason TEXT,
        tweet_published INTEGER DEFAULT 0,
        insta_published INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(article_id) REFERENCES articles(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        url TEXT,
        path TEXT,
        FOREIGN KEY(post_id) REFERENCES posts(id)
    )""")
    conn.commit()
