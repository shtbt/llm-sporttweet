import time
from datetime import datetime
from utils import fetch_top_sports_news, process_news_item, decide_non_urgent_posts, post_non_urgent

if __name__ == "__main__":
    while True:
        print(f"[{datetime.now()}]===[RUNNING]===")
        try:
            #Fetching New Articles
            news_items = fetch_top_sports_news()
            for item in news_items:
                process_news_item(item["title"], item["url"], item["published"], item["published_dt"])
        except Exception as e:
            print(f"[MAIN ERROR] {e}")

        try:
            # Process each article
            for article_id in decide_non_urgent_posts():
                post_non_urgent(article_id)
        except Exception as e:
            print(f"[NON-URGENT ERROR] {e}")

        print("[WAIT] Sleeping for 5 minutes...\n")
        time.sleep(5 * 60)