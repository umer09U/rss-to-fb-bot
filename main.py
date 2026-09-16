import os
import feedparser
import requests

# GitHub Secrets سے حساس معلومات لینا
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")

# یہاں اپنی نیوز ویب سائٹ کا اصل RSS فیڈ لنک ڈالیں
RSS_URL = "https://your-rss-feed-url.com/rss"


def get_latest_news():
  feed = feedparser.parse(RSS_URL)
  if feed.entries:
    latest = feed.entries[0]
    return latest.title, latest.description, latest.link
  return None, None, None


def generate_with_gemini(title, description):
  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
  prompt = f"Check this news from RSS: Title: {title} and Description: {description}. Verify context, extract top SEO keywords, and rewrite it into a professional Facebook post style for 'FC Balochtan'. Add hashtags at the end."

  payload = {"contents": [{"parts": [{"text": prompt}]}]}
  response = requests.post(url, json=payload)

  if response.status_code == 200:
    res_data = response.json()
    try:
      return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
      return title
  return title


def post_to_facebook(message, link):
  url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
  full_message = f"{message}\n\nRead more: {link}"
  payload = {
      "message": full_message,
      "access_token": FB_PAGE_ACCESS_TOKEN,
  }
  response = requests.post(url, data=payload)
  print("Facebook Response:", response.text)


if __name__ == "__main__":
  title, description, link = get_latest_news()
  if title:
    print("Generating post with Gemini...")
    post_text = generate_with_gemini(title, description)
    print("Posting to Facebook...")
    post_to_facebook(post_text, link)
  else:
    print("No news found.")
