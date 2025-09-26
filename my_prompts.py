from langchain_core.output_parsers.json import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

# === Prompt Templates ===

TWITTER_PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
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
""")

SCORING_PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
You are a sports news classifier. Given a news article (title + content), determine if it is about *association football (soccer)* (not American football or other sports). 
Then evaluate its proximity, freshness, and impact.

### STEP 1: Soccer relevance
Check explicitly if the news is about association football.  
- Look for soccer-specific entities: 
  - Clubs: (Manchester United, Real Madrid, Barcelona, Bayern Munich, Juventus, PSG, Arsenal, Liverpool, Chelsea, AC Milan, Inter, Dortmund, Atletico, etc.)  
  - Players: (Lionel Messi, Cristiano Ronaldo, Kylian Mbappé, Erling Haaland, Mohamed Salah, Neymar, Kevin De Bruyne, Harry Kane, Gianluigi Donnarumma, etc.)  
  - Competitions: (Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, Europa League, Conference League, World Cup, Copa America, Euro, AFCON, etc.)  
  - Organizations: (FIFA, UEFA, CAF, CONMEBOL, CONCACAF, AFC, FA, etc.)  
If the article is about basketball, American football, hockey, baseball, fantasy football, horse racing, etc., mark it as **not relevant**.

### STEP 2: Proximity (0.0–1.0)
- **1.00**: Directly and fully about association football.  
- **0.7–0.9**: Mostly about soccer but with some general sports context.  
- **0.4–0.6**: Mentions soccer but is mostly about other sports or general sports rules.  
- **0.1–0.3**: Very weak/indirect link to soccer.  
- **0.0**: Not about soccer at all.  

### STEP 3: Freshness (0–10)
- **10**: Breaking news (hours ago, "just happened", "today").  
- **7–9**: Same day or very recent.  
- **4–6**: 1–2 days old.  
- **0–3**: Stale, older, or timeless analysis.  

### STEP 4: Impact (0–10)
If “soccer_relevance” is false, set impact = 0. Otherwise assess:

* **10**: Global-major story (star transfer, World Cup/Champions League final, player injury at top level, FIFA/UEFA major rulings).  
* **8–9**: Big European league headline (Premier League, La Liga, Serie A, Bundesliga, Ligue 1), or major international-match event; or a superstar even if abroad.  
* **6–7**: Important but less global; high interest matches in Big Five or major tournament stages, famous names, big derbies.  
* **4–5**: Moderate interest; smaller leagues, less famous clubs, secondary tournaments.  
* **1–3**: Minor relevance to general soccer audience; niche, local, fantasy, betting, etc.  
* **0**: Not about soccer.

---

Now classify the following:

Title: {title}  
Content: {content}  
current_datetime: {current_datetime}
article_received_datetime: {article_received_datetime}

Respond only with a JSON object:
{{
  "soccer_relevance": true or false,
  "proximity": <float between 0 and 1.0>,
  "freshness": <0–10>,
  "impact": <0–10>
}}
""")

UNIQUENESS_PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
You are helping decide whether a news item is unique compared to previously posted ones.

Current news:
"{current_title}"

Previously posted items:
{history}

Question: Is the current news meaningfully different from the past items, or is it a duplicate/rewording of them?

Answer only in JSON:
{{
  "uniqueness": 0 or 1
}}
""")