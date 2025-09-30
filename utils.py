import os
import sqlite3
import requests
import feedparser
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from telethon import TelegramClient
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers.json import JsonOutputParser
from my_prompts import *
from db import DB_PATH
import configparser
import tweepy 
import asyncio

# ------------------------
#   General Parameters
# ------------------------

## Maximum number of non-urgent daily posts
DAILY_QUOTA = 25

## Thresolds for deciding about urgent posts
INSTANT_THRESHOLD = {"freshness": 8, "impact": 7, "uniqueness":1,"proximity": 0.8}

### Set to telegram, if you wanna send posts to your 
### telegram saved message or any id you have set for TELEGRAM_ADMIN in config.ini
### Set to twitter if you want to post directly to twitter.
### Set to Both if you want only save in DB
### Set to None if you want only save in DB
POST_MODE = 'telegram'

# ------------------------
#   Config
# ------------------------
config = configparser.ConfigParser()
config.read_file(open(r'config.ini'))

# ------------------------
#   Twitter API Credentials
# ------------------------
try:
    twitter_api=None
    TW_CONSUMER_KEY = config.get('TWITTER_API', 'TW_CONSUMER_KEY')
    TW_CONSUMER_SECRET = config.get('TWITTER_API', 'TW_CONSUMER_SECRET')
    TW_ACCESS_TOKEN = config.get('TWITTER_API', 'TW_ACCESS_TOKEN')
    TW_ACCESS_SECRET = config.get('TWITTER_API', 'TW_ACCESS_SECRET')

    #if all of the keys are not None
    if TW_CONSUMER_KEY and TW_CONSUMER_SECRET and TW_ACCESS_TOKEN and TW_ACCESS_SECRET:
        auth = tweepy.OAuth1UserHandler(
            TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET
        )
        try:
            twitter_api = tweepy.API(auth)
        except Exception as ex:
            print('Error Connecting to Twitter')
except Exception as ex:
    print(f'Error setting credentials for Twitter(X): {ex}')


# ------------------------
#   Telegram API Credentials
# ------------------------
try:
    telegram_client = None
    API_ID = int(config.get('TELEGRAM_API', 'API_ID'))
    API_HASH = config.get('TELEGRAM_API', 'API_HASH')
    SESSION_NAME = config.get('TELEGRAM_API', 'SESSION_NAME')
    TELEGRAM_ADMIN = config.get('TELEGRAM_API', 'TELEGRAM_ADMIN')   # "me" means your own account

    async def get_telegram_client():
        global telegram_client
        if telegram_client is None:
            telegram_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
            await telegram_client.start()
        return telegram_client
except Exception as ex:
    print(f'Error setting credentials for Telegram: {ex}')



# ------------------------
#   LLM Model
# ------------------------
llm_model = ChatOllama(model="gemma3:4b-it-q8_0", temperature=0, num_ctx=65535)
parser = JsonOutputParser()


# ------------------------
#   Twitter API Sender
# ------------------------
def post_to_twitter(tweet_text):
    try:
        twitter_api.update_status(status=tweet_text)
        print(f"[TWITTER] ✅ Tweet posted")
    except Exception as e:
        print(f"[TWITTER ERROR] {e}")


# ------------------------
#   Telegram API Sender
# ------------------------
def send_to_telegram_via_telethon(message):
    """Send draft tweet to admin via Telethon."""
    async def _send():
        try:
            client = await get_telegram_client()
            await client.send_message(TELEGRAM_ADMIN, message)
            print("[TELETHON] ✅ Sent to admin")
        except Exception as e:
            print(f"[TELETHON ERROR] {e}")

    # Run in event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(_send())
        else:
            loop.run_until_complete(_send())
    except RuntimeError:
        asyncio.run(_send())


# ------------------------
#   LLM Scoring & Tweets
# ------------------------
def score_article_with_llm(url, title, content, history, article_received_datetime):
    try:
        chain = SCORING_PROMPT_TEMPLATE | llm_model | parser
        scores = chain.invoke({
            "title": title,
            "content": content[:500],
            "current_datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "article_received_datetime": article_received_datetime.strftime("%Y-%m-%d %H:%M:%S")
        })
        soccer_relevance=scores['soccer_relevance']
        proximity=scores['proximity']
        freshness=scores['freshness']
        impact=scores['impact']

        chain = UNIQUENESS_PROMPT_TEMPLATE | llm_model | parser
        unq_answer = chain.invoke({
            "current_title": title,
            "history": "\n".join(history)
        })
        uniqueness=unq_answer['uniqueness']
        scores['uniqueness']=uniqueness
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE articles 
                   SET proximity=?, freshness=?, impact=?, uniqueness=? WHERE url = ?""",
                (
                    proximity,
                    freshness,
                    impact,
                    uniqueness,
                    url
                ),
            )
            conn.commit()
        return scores
    except Exception as e:
        print(f"[LLM ERROR] Worthiness check failed: {e}")
        return {k: -1 for k in ["proximity","freshness","impact","uniqueness"]}


def generate_tweet(title, content):
    try:
        chain = TWITTER_PROMPT_TEMPLATE | llm_model
        return chain.invoke({"title": title, "content": content}).content.strip()
    except Exception as e:
        print(f"[LLM ERROR] Tweet generation failed: {e}")
        return ""


def _compose_tweet_with_url(text, url, max_chars=250):
    """Truncate tweet safely before adding URL."""
    budget = max_chars - 24  # reserve for URL
    t = text.strip()
    if len(t) > budget:
        t = t[:max(budget - 1, 0)].rstrip() + "…"
    return f"{t}\n{url}"


# ------------------------
#   RSS + Scraping
# ------------------------
def fetch_top_sports_news():
    feeds = [
        "https://www.espn.com/espn/rss/news",
        "https://www.skysports.com/rss/12040",
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.fourfourtwo.com/feeds.xml"
    ]
    results = []
    for feed_url in feeds:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                if entry.get("published_parsed"):
                    dt_local = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed), tz=timezone.utc
                    )
                    hours_passed = (datetime.now(timezone.utc) - dt_local).total_seconds() / 3600
                    if hours_passed > 12:
                        continue
                else:
                    dt_local = datetime.now(timezone.utc)
                results.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "published_dt": dt_local,
                })
        except Exception as e:
            print(f"[RSS ERROR] {feed_url} → {e}")
    return results


def save_article_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        text = "\n".join(p.get_text() for p in soup.find_all("p") if p.get_text())
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE articles SET content = ? WHERE url = ?", (text, url))
            conn.commit()
        return text
    except Exception as e:
        print(f"[SCRAPE ERROR] {url} → {e}")
        return ""


# ------------------------
#   DB Utilities
# ------------------------
def article_already_processed(url):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        return cursor.fetchone() is not None


def get_today_articles_not_posted():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""select
        id,title,content,proximity,freshness,impact,engagement,uniqueness,virality
            FROM articles WHERE date(received_at) = date('now') and posted=0
        """)

        ret=[
            {"id":row[0],"title":row[1],"content":row[2],"proximity":row[3],"freshness":row[4],"impact":row[5],
        "engagement":row[6],"uniqueness":row[7],"virality":row[8]
        } 
            for row in cursor.fetchall()]
        return ret if len(ret)!=0 else []


def get_today_post_history():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT caption FROM posts WHERE date(created_at) = date('now')
        """)
        ret=[row[0] for row in cursor.fetchall()]
        return ret if len(ret)!=0 else []

# === Post Quota and History ===
def get_today_post_count():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts WHERE date(created_at) = date('now')")
        return cursor.fetchone()[0]

def save_rss_item(title, url, published):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO articles (title, url, published_at)
            VALUES (?, ?, ?)
        """, (title, url, published))
        conn.commit()


def save_post(article_url, caption, tweet, reason):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM articles WHERE url = ?", (article_url,))
        row = cursor.fetchone()
        if not row:
            print(f"[ERROR] Article not found for post.")
            return None
        article_id = row[0]
        cursor.execute("""
            INSERT INTO posts (article_id, caption, tweet, reason)
            VALUES (?, ?, ?, ?)
        """, (article_id, caption, tweet, reason))
        conn.commit()
        return cursor.lastrowid


# ------------------------
#   Main Handlers
# ------------------------
def process_news_item(title, url, published, published_dt):
    if article_already_processed(url):
        print(f"[{datetime.now()}][SKIP] Already processed: {title}")
        return

    print(f"[{datetime.now()}][NEW] Processing: {title}")
    save_rss_item(title, url, published)
    content = save_article_content(url)

    if not content or len(content.strip()) < 400:
        print(f"[SKIP] Content too short.")
        return

    scores = score_article_with_llm(
        url=url,
        title=title,
        content=content,
        history=get_today_post_history(),
        article_received_datetime=published_dt
    )

    if get_today_post_count() < DAILY_QUOTA and should_post_instant(scores):
        post_article(url, title, content)



def should_post_instant(scores):
    return (
        scores["freshness"] >= INSTANT_THRESHOLD["freshness"] and
        scores["impact"] >= INSTANT_THRESHOLD["impact"] and
        scores["uniqueness"] >= INSTANT_THRESHOLD["uniqueness"] and
        scores["proximity"] >= INSTANT_THRESHOLD["proximity"] 
    )


def post_article(url, title, content, reason="instant"):
    print(f"POSTING: {title}")
    raw = generate_tweet(title, content)
    tweet = _compose_tweet_with_url(raw, url)
    save_post(url, tweet, tweet, reason)

    if POST_MODE == "twitter":
        post_to_twitter(tweet)
    elif POST_MODE == "telegram":
        send_to_telegram_via_telethon(tweet)
    elif POST_MODE.lower() == "both":
        post_to_twitter(tweet)
        send_to_telegram_via_telethon(tweet)
    else:
        pass

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE articles SET posted = 1 WHERE url = ?", (url,))
        conn.commit()


def decide_non_urgent_posts():
    candidate_posts = get_today_articles_not_posted()
    already_posted_today = len(get_today_post_history())
    remaining_capacity = max(0, DAILY_QUOTA - already_posted_today)
    if remaining_capacity <= 0:
        return []

    # Step 1: Keep only true soccer posts (proximity == 10, fresh, unique)
    filtered = [
        p for p in candidate_posts
        if p.get("proximity", 0) >= 0.8
        and p.get("freshness", 0) >= 6
        and p.get("uniqueness", 0) == 1
    ]
    if not filtered:
        return []

    # Step 2: Split into high-impact (≥7) vs. low-impact (<7, e.g., MLS)
    high_impact = [p for p in filtered if p.get("impact", 0) >= 7]
    low_impact = [p for p in filtered if p.get("impact", 0) < 7]

    # Step 3: Select posts, prioritizing high-impact first
    selected = []
    if high_impact:
        k = min(len(high_impact), remaining_capacity)
        selected.extend(random.sample(high_impact, k=k))
        remaining_capacity -= k

    # Step 4: If quota still available, allow low-impact posts (MLS, etc.)
    if remaining_capacity > 0 and low_impact:
        k = min(len(low_impact), remaining_capacity)
        selected.extend(random.sample(low_impact, k=k))

    return [p["id"] for p in selected]


def post_non_urgent(article_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT url, title, content FROM articles WHERE id = ?", (article_id,))
    row = cur.fetchone()
    if not row:
        return
    url, title, content = row
    print(f"POSTING: {title}")
    raw = generate_tweet(title, content)
    tweet = _compose_tweet_with_url(raw, url)
    save_post(url, tweet, tweet, 'non-urgent')

    if POST_MODE == "twitter":
        post_to_twitter(tweet)
    elif POST_MODE == "telegram":
        send_to_telegram_via_telethon(tweet)

    cur.execute("UPDATE articles SET posted = 1 WHERE id = ?", (article_id,))
    conn.commit()


