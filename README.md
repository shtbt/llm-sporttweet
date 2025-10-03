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
0. [Prerequisites](#prerequisites)
1. [Quick Start](#quick-start)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Full Article](#full-article)

---
##  ⏪Prerequisites
Before running this project, make sure you have [Ollama](https://github.com/ollama/ollama/tree/main/docs) installed. You can find detailed instruction for installing ollama in [this medium post](https://medium.com/@hassan.tbt1989/build-a-rag-powered-llm-service-with-ollama-open-webui-a-step-by-step-guide-a688ec58ac97), but in short, to run Ollama in a containerized environment, we will set it up using Docker. See installation instruction here.

**In each step, use ```sudo``` if needed**
### 1. Install Docker
Before proceeding, make sure you have Docker installed. If not, install it using the following commands:
- **For Linux (Debian/Ubuntu):**  
  ```bash
  sudo apt update && sudo apt install -y docker.io
  ```
- **For macOS (via Homebrew):**
  ```bash
  brew install docker
  ```
- **For Windows:**
  Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) from Docker’s official website. Or you can use WSL to emulate Linux.
### 2. Pull the Ollama Docker Image
Once Docker is installed, pull the latest Ollama image(Use sudo if needed):
  ```bash
  sudo docker pull ollama/ollama:latest
  ```
### 3. Run Ollama Container
Now, start the Ollama container with the necessary configurations:
```bash
sudo docker run -d --name ollama \
  --gpus=all \
  -p 11434:11434 \
  -v ollama_data:/root/.ollama \
  ollama/ollama:latest
```

### 4. Verify the Installation
To check if Ollama is running, use:
```bash
sudo docker ps
```
You should see the ollama container running.

### 5. Pulling a model in ollama
Now that you have everything set, you need to pull a model for ollama. choose your model from [ollama models repository](https://ollama.com/search). Pay attention to the capacity of your machine and choose the suitable version of the model. Pay attention to the capacity of your machine and choose the suitable version of the model. I have choosen ```gemma3:4b-it-q8_``` . For downloading the model:
```bash
sudo ollama pull gemma3:4b-it-q8_0
```


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
For **Twitter (X)**, create a developer account at [developer.x.com](https://developer.x.com/), apply for a project/app, and generate your **API Key**, **API Secret Key**, **Access Token**, and **Access Token Secret**. For **Telegram**, go to [my.telegram.org](https://my.telegram.org/), log in with your account, and under API Development Tools, create a new application to get your **API ID** and **API Hash**. You’ll also need to set a **SESSION_NAME** (any identifier for your session) and define **TELEGRAM_ADMIN** as the Telegram ID of the account that should receive the tweets. If you set it to **`me`**, the messages will be sent to your **Saved Messages**. ⚡ On the first run of the Telegram client, you’ll be asked to enter your phone number. Telegram will then send you a one-time code for verification. This happens only during the initial setup. Once your session is created, you won’t be asked again for your phone or token in subsequent runs. Both sets of credentials _**should be stored securely**_.
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
python3 main.py
```
* The bot runs continuously, checking RSS feeds every 5 minutes.
* It scores articles via Ollama + LangChain and decides which tweets to send—either posting directly or drafting to Telegram.

## 🛠Features

* Fetches sports news from RSS feeds
* Scrapes and stores articles in SQLite
* Uses LLM (Ollama + LangChain) to evaluate worthiness
* Generates Twitter-ready captions (urgent + non-urgent)
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

Every day, sports journalists, bloggers, and fans sift through endless streams of football news - most of which never makes it to a post. Deciding what's truly worth sharing takes time, attention, and effort.
That's where Large Language Models (LLMs) change the game. Unlike simple automation scripts or keyword filters, LLMs can actually **read the text, evaluate its importance, and judge whether it's worth publishing**. They go beyond summarizing - they apply reasoning, judgment, and creativity to turn raw news into engaging content.

With this system, I built a pipeline that **separates soccer news from other stories, filters out the noise, and highlights only the most valuable articles**. Each news item is scored on multiple dimensions - such as proximity, freshness, impact, and uniqueness - so that only the most relevant and engaging pieces are turned into social media posts.
The pipeline runs fully locally using **Ollama for LLM inference, SQLite for structured storage**, and **LangChain as the orchestration layer**. It acts like a miniature autonomous newsroom: crawling feeds, evaluating newsworthiness, generating captions, and preparing Twitter-ready (or Instagram) posts.
While I focus on **football(soccer) news** here, this workflow can easily be adapted to other domains - whether it's technology, finance, science, or any project that requires filtering large information streams and posting only the best.

## **🚀 How the Pipeline Works (Step by Step)**

1. **Start the Main Loop**  
    The app runs continuously, checking for fresh news every 5 minutes and pulls articles from RSS feeds (like ESPN, SkySports, BBC).  
2. **Scrape Full Article Text**  
    Each new article's title, URL, and timestamp are being saved then we download the webpage and extracts readable text with BeautifulSoup and save them. Short or empty articles are skipped to maintain quality.  
3. **Score with LLM**  
    The article content goes through LLM which uses Ollama + LangChain to assign four scores: proximity, freshness, impact, uniqueness. These scores are stored back into the sqlite DB for decision-making.  
4. **Decide on Instant Posting**  
    If the article is highly fresh, impactful, viral, and football-related, we decide to immediately post that.  
5. **Generate Instant Tweet Text And Post Accordingly**  
   If we decide to post the news immediately, we create a short, engaging tweet using the Twitter prompt template  and safely appends the article link without exceeding 250 characters. Depending on config, the bot either posts the tweet to X (Formerly Twitter), or sends the draft to Telegram (for human observation) and logs the tweet, caption, reason, and article reference in the Database.  
6. **Select Non-Urgent Candidates**  
   After scoring all of the newly-crawled news and deciding about instant tweets, we pick a few strong but non-urgent news, and generating tweets of them with LLM, respecting the daily quota. We may wont pick any new tweet. Then we publishes selected candidates later in the day, spacing out updates. We ensure the bot never posts more than a **certain amount** times per day.  
7. **Sleep & Repeat**  
    Finally, the bot sleeps for 5 minutes before starting the cycle again.

![Pipeline of the Project](/img/pipeline.png)**Pipeline of the Project**

## **⚡ Scoring & Tweet Generation with LLMs**
A central part of the system is the way I use **LLM prompts** for two tasks: scoring news items and generating platform-ready text.
### **Scoring**
Instead of relying on a rigid rule-based engine, I ask the model to evaluate each article across four dimensions:

* **Proximity**: How closely the news is related to football (soccer).  
* **Freshness**: Whether the story is recent or breaking compared to the current date and time.  
* **Impact**: Its importance for fans — big clubs, star players, or title races.  
* **Uniqueness**: How distinct it is compared to that day’s post history.

To make these evaluations reliable, the prompts enforce **structured output**. This was critical: without it, the model might generate free-form text that is hard to parse programmatically. With structured JSON responses, I can extract consistent values that flow directly into the automation pipeline, reducing errors and ensuring decisions are reproducible.
Another lesson I've learnt is that I shouldn't **overload a single prompt**. Initially I combined all scoring dimensions (soccer relevance, freshness, impact, uniqueness) into one monster instruction. That backfired - especially uniqueness, since I was feeding both current and historical titles, which made the model "**forget**" the main scoring task. So I split the logic into two clear prompts:
* **Scoring Prompt**, which checks **Proximity**, **Freshness** and **Impact**. 
* **Uniqueness Prompt**, which compares the **current article title** with a short history of already-posted items
I feed only first 500 characters of the article to the **SCORING_PROMPT_TEMPLATE** in order to prevent hallucination which may cause from long input to the small-middle size models. Here's the schema I embedded directly in the scoring prompt:
```json
{  
 "proximity": "number between 0-10",  
 "freshness": "number between 0-10",  
 "impact": "number between 0-10"
}
```

```json
{  
 "uniqueness": "number between 0-10"
}
```
finally, we set a criteria based on this scores for accepting a news as urgent and post it immediately.

```python
INSTANT_THRESHOLD = {"freshness": 8, "impact": 7, "uniqueness":1,"proximity": 0.8}
...
def should_post_instant(scores):
    return (
        scores["freshness"] >= INSTANT_THRESHOLD["freshness"] and
        scores["impact"] >= INSTANT_THRESHOLD["impact"] and
        scores["uniqueness"] >= INSTANT_THRESHOLD["uniqueness"] and
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
```

### **Tweet Generation**
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


To make these evaluations reliable, the prompts enforce **structured output**. This was critical: without it, the model might generate free-form text that is hard to parse programmatically. With structured JSON responses, I can extract consistent values that flow directly into the automation pipeline, reducing errors and ensuring decisions are reproducible. Here’s the schema I embedded directly in the scoring prompt:

```json
{  
 "proximity": "number between 0-10",  
 "freshness": "number between 0-10",  
 "impact": "number between 0-10",  
 "uniqueness": "number between 0-10"
}
```
### **LLM Model**
Since I'm running this on a personal machine with an **RTX 3060 (8 GB VRAM)**, I had to be mindful of model size and memory requirements. After testing different options, I settled on **gemma3:4b-it-q8_0** - a quantized, instruction-tuned model. It's small enough to fit comfortably on my GPU, while still being powerful enough to handle scoring and text generation tasks. For anyone without a GPU, you can still run **Ollama** on a CPU system - it just runs slower, but it works! That means this project is accessible even if you only have a modest VPS or laptop.

### **Feeding the Model: Less Is More**
At first, I naively sent **entire articles** to the LLM for scoring. The results were disappointing: long contexts made the model inconsistent, and responses were noisy.
 The solution? I trimmed input down to just the **first ~500 characters** of each article. That short snippet usually contains the headline and lead, which is enough for the model to judge relevance, freshness, and impact. The scoring became much more accurate and stable after this change.

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
  "proximity": 0.9,
  "freshness": 8,
  "impact": 9,
  "uniqueness": 9
}
```
Also, you can explore `content_creator.db` which is our sqlite database and has stored tables: articles and posts.

## **💻 Code & Repository**

All the code for this project is available on GitHub. You can explore it, try it yourself, or adapt it for your own use cases:

**GitHub:** [https://github.com/shtbt/llm-newsroom](https://github.com/shtbt/llm-newsroom)

## **🔮 What’s Next**

This pipeline already filters football news and generates Twitter posts automatically, but the journey doesn't stop here. There are several exciting directions to make it smarter, faster, and more versatile:
* **Embedding-Based Uniqueness Checks:** Instead of relying solely on LLM calls to measure uniqueness, I plan to integrate an **embedding model** to detect similarity between articles. This reduces redundant LLM calls, cuts down expenses, and makes the system more scalable.
* **Smarter Prompt Engineering:** Prompts are the "control knobs" of an LLM system. By refining them, I can improve scoring accuracy, make generated captions more engaging, and fine-tune the tone for different audiences. Better prompts = better posts without touching the underlying code.
* **Instagram + Images :** Beyond Twitter, the system can soon support **Instagram posting**, complete with auto-generated captions and **relevant images** scraped and selected alongside the news. With both text and visuals, the pipeline becomes a true multi-platform content creator.
* **Richer Content Types:** This approach isn't limited to breaking news. The same scoring-and-generation workflow can be extended to** weekly roundups, "on-this-day" historical throwbacks**, or even **summaries of long-form articles**. With structured scoring and filtering, the bot can adapt to any content style.
These possibilities show how flexible LLM-powered pipelines can be. By adjusting prompts and scoring logic, the system can handle multiple platforms, content formats, and even entirely new domains.

## **🏁 Conclusion**

This project shows that **LLMs are not just chatbots** - they can serve as **autonomous editors, curators, and creators**. With the right combination of **prompts, scoring logic, embeddings, and automation**, an LLM-powered pipeline can read raw news, evaluate its importance, and transform it into engaging social media content with minimal human effort.
By integrating **RSS feeds, structured scoring, and post generation**, I built a system that continuously turns streams of soccer news into ready-to-publish Twitter and Instagram content. What once required hours of editorial work can now run on its own - making both judgment calls and creative choices automatically. But this is only the beginning. The same framework can be extended to:

* **Instagram with captions + images**
* **Blogs and newsletters**
* **Multi-lingual newsrooms**
* **Other domains like finance, technology, or science**

## **📬 Let's Connect**
⚡ In short, this project is a blueprint for LLM-powered content automation - a glimpse of how future newsrooms, brands, and creators can scale their voices without scaling their teams.
If you're interested in collaborating, sharing feedback, or exploring similar projects, feel free to reach out:
* **Email**: [hassan.tbt1989@gmail.com](mailto:hassan.tbt1989@gmail.com)
* **GitHub Repo of the Project**: [https://github.com/shtbt/llm-newsroom](https://github.com/shtbt/llm-newsroom)
* **LinkedIn**: [https://www.linkedin.com/in/s-hassan-tabatabaei-19b5298a](https://www.linkedin.com/in/s-hassan-tabatabaei-19b5298a/)
