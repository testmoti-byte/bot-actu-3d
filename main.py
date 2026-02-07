import os
import sys
import json
import requests
import feedparser
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import video_animator
from video_animator import creer_video_article

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
IDS_STR = os.getenv("TELEGRAM_CHAT_IDS", "")
LISTE_ID = [id.strip() for id in IDS_STR.split(",") if id.strip()]

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "VIDEO" # Corrigé selon ta capture
CACHE_FILE = BASE_DIR / "articles_cache.json"

def generer_script_ia(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Flash info 3D : découvrez les dernières innovations."

def scraper_rss():
    articles = []
    url = "https://www.3dnatives.com/fr/feed/"
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]:
        articles.append({
            "source": "3D Natives",
            "title": entry.get('title', 'Sans titre'),
            "link": entry.get('link', ''),
            "summary": entry.get('summary', '')[:300]
        })
    return articles

def envoyer_telegram(video_path, article):
    message = f"🎙 **{article['title']}**\n📡 Source: {article['source']}"
    for chat_id in LISTE_ID:
        with open(video_path, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", 
                          data={'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'},
                          files={'video': v})

def traiter_articles():
    cache = set(json.load(open(CACHE_FILE)) if CACHE_FILE.exists() else [])
    nouveaux = [a for a in scraper_rss() if a['link'] not in cache]
    
    if not nouveaux:
        nouveaux = [{"source": "CULTURE 3D", "title": "Le saviez-vous ?", "link": "https://3dn.com", "is_anecdote": True}]

    for article in nouveaux[:1]:
        # ON FORCE ELISE ET LE BUREAU
        avatar = "elise_neutre.png"
        script = generer_script_ia("Fais un script de 20s sur l'impression 3D.")
        article['script_jt'] = script
        chemin_avatar = str(IMAGES_DIR / avatar)
        
        video = creer_video_article(article, chemin_avatar)
        if video:
            envoyer_telegram(video, article)
            cache.add(article['link'])

    with open(CACHE_FILE, 'w') as f:
        json.dump(list(cache), f)

if __name__ == "__main__":
    traiter_articles()
