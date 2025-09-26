# 📌 LLM-Newsroom
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
![LangChain](https://img.shields.io/badge/Powered%20by-LangChain-green) 
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange) 
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)
![Repo Size](https://img.shields.io/github/repo-size/shtbt/llm-newsroom)
![Last Commit](https://img.shields.io/github/last-commit/shtbt/llm-newsroom)


### An Autonomous LLM-powered newsroom that reads sports news feeds, scores articles, and writes its own tweets 🤖
*Automates content curation, scoring, and social media posting using LLMs.*

![LLM-Newsroom](/img/header.png)
---

## Table of Contents
1. [Quick Start](#quick-start)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Full Article](#full-article)

---

##  🚀Quick Start

###  1. Clone the Repository & Install Dependencies
```bash
git clone https://github.com/shtbt/llm-newsroom.git
cd llm-newsroom
pip install -r requirements.txt
```

###  2. Configure credentials
Copy the sample configuration file and add your API keys:
```bash
cp config.sample.ini config.ini
```
Then open config.ini and update the following sections with your credentials:
```ini
[TWITTER_API]
TW_CONSUMER_KEY=YOUR_API_KEY
TW_CONSUMER_SECRET=YOUR_API_SECRET
TW_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
TW_ACCESS_SECRET=YOUR_ACCESS_SECRET

[TELEGRAM_API]
API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
SESSION_NAME=YOUR_SESSION_NAME
TELEGRAM_ADMIN=YOUR_CHAT_ID
```
### 3. Run the Pipeline
```bash
python main.py
```
* The bot runs continuously, checking RSS feeds every 5 minutes.
* It scores articles via Ollama + LangChain and decides which tweets to send—either posting directly or drafting to Telegram.

## 🛠Features

* Fetches sports news from RSS feeds
* Scrapes and stores articles in SQLite
* Uses LLM (Ollama + LangChain) to evaluate worthiness
* Generates Twitter-ready captions (urgent + non-urgent)
* Supports image downloads for posts
* Avoids reposting and duplicates


## 📂Project Structure
```arduino
llm-newsroom/
│─── main.py              # entry point
│─── utils.py             # helper scripts
│─── db.py                # sqlite schema & migrations
│─── my_prompts.py        # LLM prompts
│─── config.ini           # Config file for setting Twitter and Telegram Developer Tokens
│... content_creator.db   # Sqlite DB for storage of data
│─── requirements.txt
│─── README.md
```

## 📖Full Article

This project was originally explained in detail on Medium:
👉 ***LLM-Newsroom: How I Built an Autonomous LLM Pipeline That Reads Sports News and Writes Its Own Tweets***

Below is the full article for accessibility:

# LLM-Newsroom: How I Built an Autonomous LLM Pipeline That Reads Sports News and Writes Its Own Tweets

![LLM-Newsroom](/img/llm-newsroom-cover.png)**LLM-Newsroom**



## **🚀 Introduction**

Every day, newsrooms, bloggers, and sports fans spend hours scanning feeds, summarizing stories, and rewriting them into social media posts. It’s valuable work, but also repetitive and mechanical.

Large Language Models (LLMs) are changing that. Unlike traditional automation scripts or rule-based systems, LLMs can **read raw text, evaluate its importance, and generate content that feels human**. They don’t just process information — they apply reasoning, judgment, and creativity. That makes them ideal for tasks like turning streams of football news into engaging tweets.

So I set out to build something different: an **autonomous LLM-powered pipeline** that behaves like a miniature newsroom. It reads news feeds, decides what’s worth sharing, scores each article across multiple dimensions (freshness, impact, virality, uniqueness, and more), and finally writes its own tweets — either posting instantly or queuing them for later.

The best part? It runs fully locally using **Ollama for LLM inference, SQLite for structured storage, and a clean Python pipeline with LangChain as the glue**. This isn’t just a demo — it’s a practical showcase of how LLMs can act as reasoning engines, content creators, and decision-makers in an end-to-end automated workflow.

In this article, I’ll walk you through how I built it — from feeds to tweets — and how you can extend it into your own autonomous newsroom.

## **🚀 How the Pipeline Works (Step by Step)**

1. **Start the Main Loop**  
    The app runs continuously, checking for fresh news every 5 minutes and pulls articles from RSS feeds (like ESPN, SkySports, BBC).  
2. **Scrape Full Article Text**  
    Each new article’s title, URL, and timestamp are being saved then we download the webpage and extracts readable text with BeautifulSoup and save them. Short or empty articles are skipped to maintain quality.  
3. **Score with LLM**  
    The article content goes through LLM which uses Ollama \+ LangChain to assign six scores: proximity, freshness, impact, engagement, uniqueness, and virality. These scores are stored back into the sqlite DB for decision-making.  
4. **Decide on Instant Posting**  
    If the article is highly fresh, impactful, viral, and football-related, we decide to immediately post that.  
5. **Generate Instant Tweet Text And Post Accordingly**  
   If we decide to post the news immediately, we create a short, engaging tweet using the Twitter prompt template and safely appends the article link without exceeding 250 characters. Depending on config, the bot either posts the tweet to X (Formerly Twitter), or sends the draft to Telegram (for human observation) and logs the tweet, caption, reason, and article reference in the Database.  
6. **Select Non-Urgent Candidates**  
   After scoring all of the newly-crawled news and deciding about instant tweets, we pick a few strong but non-urgent news, and generating tweets of them with LLM, respecting the daily quota. We may wont pick any new tweet. Then we publishes selected candidates later in the day, spacing out updates. We ensure the bot never posts more than a **certain amount** times per day.  
7. **Sleep & Repeat**  
    Finally, the bot sleeps for 5 minutes before starting the cycle again.

![Pipeline of the Project](/img/pipeline.png)**Pipeline of the Project**

## **⚡ Scoring & Tweet Generation with LLMs**

A central part of the system is the way I use **LLM prompts** for two tasks: scoring news items and generating platform-ready text. Instead of relying on a rigid rule-based engine, I ask the model to evaluate each article across six dimensions:

* **Proximity**: How closely the news is related to football (soccer).  
* **Freshness**: Whether the story is recent or breaking compared to the current date and time.  
* **Impact**: Its importance for fans — big clubs, star players, or title races.  
* **Engagement**: Likelihood of sparking reactions, shares, or discussions.  
* **Uniqueness**: How distinct it is compared to that day’s post history.  
* **Virality**: Its potential to trend or go viral on social platforms.

To make these evaluations reliable, the prompts enforce **structured output**. This was critical: without it, the model might generate free-form text that is hard to parse programmatically. With structured JSON responses, I can extract consistent values that flow directly into the automation pipeline, reducing errors and ensuring decisions are reproducible. Here’s the schema I embedded directly in the scoring prompt:

```json
{  
 "proximity": "number between 0-10",  
 "freshness": "number between 0-10",  
 "impact": "number between 0-10",  
 "engagement": "number between 0-10",  
 "uniqueness": "number between 0-10",  
 "virality": "number between 0-10",  
 "final_decision": "POST or SKIP"  
}
```

When it came to generating the actual posts, I deliberately took a different approach. Unlike the scoring phase, where **structured JSON output** was essential for automation, the generation step only needed the **final text** of the tweet. Here, creativity and readability mattered more than rigid structure. The instructions were carefully crafted to enforce **length limits, tone, and style**, while leaving room for the model’s expressive capacity.

```yaml
You are an expert football journalist and social media strategist for Twitter (X).

Write a **concise, high-impact tweet** for the sports article below.
- Max length: **250 characters** (never exceed).
- Tone: Newsworthy but engaging; spark discussion.
- If relevant, include **one football-related emoji** (⚽🔥🏆, etc.).
- Optionally add **1-2 trending hashtags** at the end.
- Avoid generic phrases like "Breaking:" unless truly urgent.
- Make the most important detail the first thing readers see.

**TITLE:** {title}  
**CONTENT:** {content}

Respond ONLY with the tweet text.
```

finally, we set a criteria based on this scores for accepting a news as urgent and post it immediately.

```python
INSTANT_THRESHOLD = {"freshness": 8, "impact": 7, "virality": 7, "proximity": 9}
...
def should_post_instant(scores):
    return (
        scores["freshness"] >= INSTANT_THRESHOLD["freshness"] and
        scores["impact"] >= INSTANT_THRESHOLD["impact"] and
        scores["virality"] >= INSTANT_THRESHOLD["virality"] and
        scores["proximity"] >= INSTANT_THRESHOLD["proximity"]
    )
```

and for non-urgent posts:

```python
def decide_non_urgent_posts():
    candidate_posts = get_today_articles_not_posted()
    already_posted_today = len(get_today_post_history())
    remaining_capacity = max(0, DAILY_QUOTA - already_posted_today)
    if remaining_capacity <= 0:
        return []

    filtered = [
        p for p in candidate_posts
        if p.get("proximity", 0) == 10
        and p.get("freshness", 0) >= 5
        and p.get("uniqueness", 0) >= 7
    ]
    if not filtered:
        return []

    ids = [p["id"] for p in filtered]
    k = min(2, remaining_capacity, len(ids))
    return random.sample(ids, k=k)
```

## **🛠️ The Tech Stack**

* **LLM Engine**: The pipeline runs on **Ollama**, a lightweight framework for serving large language models locally. I’ve previously covered how to set up Ollama in [this step-by-step guide](https://medium.com/@hassan.tbt1989/build-a-rag-powered-llm-service-with-ollama-open-webui-a-step-by-step-guide-a688ec58ac97). In this project, Ollama powers the reasoning steps (deciding whether a news item is worth sharing) and the generation tasks (drafting tweets and Telegram posts). I use the model [***gemma3:4b-it-q8\_0***](https://huggingface.co/google/gemma-3-4b-it) which can be plugged in my hardware.  
* **LangChain**: The pipeline leverages [**LangChain**](https://www.langchain.com/) to connect the LLM with data and workflow. LangChain handles prompts, output parsing, and structured interactions with the model, making it easy to feed articles into the LLM, interpret scores, and generate tweets. Essentially, it acts as the “glue” between the LLM reasoning engine, the RSS/news sources, and the database, allowing for clean, maintainable, and reusable code.  
* **Data Storage with SQLite**: All articles, scores, generated tweets, and post metadata are stored in a lightweight **SQLite** database. This allows the bot to track what’s been posted, maintain uniqueness checks, and enforce daily quotas without requiring a heavy database setup — perfect for a local, autonomous pipeline.  
* **APIs**: The bot can post tweets directly to X (formerly Twitter) via the Twitter API, or send draft posts to a designated **Telegram** account using Telethon. This gives the option of full automation or human review before publishing, while keeping all posts logged and traceable in the database.

## **⚙️ Inside the Codebase**

The pipeline is designed to be modular, with each part handling a specific responsibility. Breaking it into clear components keeps the system maintainable and makes the logic easier to follow. Here’s an overview of the main modules:

**`main.py` – The Main Loop**  
 This is the entry point of the pipeline. It runs continuously, checking RSS feeds every 5 minutes for fresh articles. Each cycle:

1. **Fetch new articles** from multiple RSS feeds (SkySports, ESPN, BBC, and more).  
2. **Process each article**: downloading content, scoring with the LLM, and deciding if it should be posted **instantly**.  
3. **Handle non-urgent posts**: selecting a few strong candidates from the remaining articles and generating posts while respecting the daily quota.

**`utils.py` – Core Processing Functions**  
 This module handles the essential tasks of the pipeline: fetching articles, scraping content, scoring them with the LLM, generating tweets, and posting via Twitter or Telegram. It also manages database operations and keeps track of quotas.

**`db.py` – Database Schema and Utilities**  
The database is implemented using **SQLite**, keeping things lightweight and easy to manage. It stores articles, scores, and generated posts, and provides simple helper functions for consistent access throughout the pipeline.

**`my_prompts.py` – Prompt Templates for Scoring and Generation**  
This module contains the **LLM prompts** used for scoring articles and generating tweets. Keeping prompts separate helps maintain clarity and makes it easy to tweak scoring criteria or tweet style without touching the pipeline logic.

## **📊 What the Bot Produces**

After running the pipeline for a few days, the bot was able to process multiple football news feeds, score articles, and generate concise tweets. Here are a few representative examples:

**Instant Tweets (High-Priority Articles):**

* ⚽🔥 *“*Real Madrid are the masters of the free transfer\! ⚽🔥🏆 From Alexander-Arnold to countless others, they consistently swoop in for world-class talent without a fee. Is this the new Raul? \#FreeTransfer \#RealMadrid  
  [https://www.bbc.com/sport/football/articles/c9wyw11w77no?at\_medium=RSS\&at\_campaign=rss](https://www.bbc.com/sport/football/articles/c9wyw11w77no?at_medium=RSS&at_campaign=rss)*”*

**Non-Urgent Tweets (Scheduled Later):**

* *“Inter Milan reveals new kit for the upcoming season — fans react to the bold new design. \#SerieA”*  
* *“Leicester City academy players shine in youth tournament, promising future stars for English football.”*

**Scoring Examples:**  
 For each article, the LLM assigns structured scores such as:
```
{  
 "proximity": 10,  
 "freshness": 8,  
 "impact": 9,  
 "engagement": 7,  
 "uniqueness": 9,  
 "virality": 8  
}
```

## **💻 Code & Repository**

All the code for this project is available on GitHub. You can explore it, try it yourself, or adapt it for your own use cases:

**GitHub:** [https://github.com/shtbt/llm-newsroom](https://github.com/shtbt/llm-newsroom)

## **🔮 What’s Next**

While this pipeline already handles football news and Twitter posts autonomously, there’s plenty of room for expansion and improvement.

* **Prompt Optimization:** Anyone can refine the LLM prompts to improve scoring accuracy, make tweet generation more engaging, or adjust the style and tone to fit different audiences. Prompt engineering remains the easiest way to boost performance without changing the core code.  
* **Instagram Integration:** The same system could be extended to generate Instagram captions, select suitable images automatically, and post directly. Combining image retrieval with caption generation would make the bot a full multi-platform content creator.  
* **Other Content Types:** Beyond breaking news, LLMs can be used to decide and generate other types of posts, such as “on-this-day” historical posts, weekly roundups, or highlights from long-form articles. The structured scoring approach can be adapted for any type of content.

These possibilities show how flexible LLM-powered pipelines can be. By adjusting prompts and scoring logic, the system can handle multiple platforms, content formats, and even entirely new domains.

## **🏁 Conclusion**

This project proves that LLMs can be much more than chatbots. With the right prompts, scoring logic, and automation pipeline, they can **act as autonomous newsrooms** — reading, evaluating, and writing content on their own.

By combining RSS feeds, structured scoring, and tweet generation, I built a system that continuously turns raw sports news into social-ready posts. What once required human editors can now run automatically, with the LLM making both the judgment calls and the creative writing.

And this is only the beginning. The same approach can be extended to Instagram, blogs, or even multi-lingual news coverage — showing how powerful and flexible LLM-powered automation can be.
