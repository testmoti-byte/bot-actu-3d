import os
import sys
import json
import requests
import feedparser
import schedule
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# --- IMPORTS DES MODULES PERSONNALISÉS ---
import video_animator
from video_animator import creer_video_article

print("✅ Module video_animator chargé avec succès !")

# --- CONFIGURATION ---
load_dotenv()
IDS_STR = os.getenv("TELEGRAM_CHAT_IDS", "")
LISTE_ID = [id.strip() for id in IDS_STR.split(",") if id.strip()]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Initialisation Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Dossiers
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "videos"
CACHE_FILE = BASE_DIR / "articles_cache.json"

for folder in [IMAGES_DIR, VIDEOS_DIR]:
    folder.mkdir(exist_ok=True)

# Sources RSS
RSS_FEEDS = {
    "3dnatives": "https://www.3dnatives.com/fr/feed/",
    "fabbaloo": "https://www.fabbaloo.com/blog/feed.xml",
}

KEYWORDS = ["impression 3d", "3d printing", "additive manufacturing", "cao", "résine", "fdm", "prototypage"]

# --- FONCTIONS ---

def generer_script_ia(prompt: str) -> str:
    """Utilise Gemini pour générer le texte du JT."""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Erreur Gemini : {e}")
        return "Bienvenue dans votre flash info 3D. Aujourd'hui, nous explorons les dernières innovations du secteur."

def scraper_rss() -> List[Dict]:
    """Récupère les articles filtrés par mots-clés."""
    articles = []
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                txt = (entry.get('title', '') + " " + entry.get('summary', '')).lower()
                if any(kw in txt for kw in KEYWORDS):
                    articles.append({
                        "source": name,
                        "title": entry.get('title', 'Sans titre'),
                        "link": entry.get('link', ''),
                        "summary": entry.get('summary', '')[:300]
                    })
        except Exception as e:
            print(f"❌ Erreur scraping {name}: {e}")
    return articles

def envoyer_telegram(video_path: str, article: Dict):
    """Envoie la vidéo finale sur Telegram."""
    message = (
        f"🎙 **FLASH INFO 3D**\n\n"
        f"📽 *{article['title']}*\n\n"
        f"🔗 [Lire l'article complet]({article['link']})\n"
        f"📡 Source : {article['source'].upper()}"
    )
    for chat_id in LISTE_ID:
        try:
            with open(video_path, 'rb') as v:
                url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
                payload = {'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'}
                files = {'video': v}
                requests.post(url, data=payload, files=files, timeout=150)
            print(f"✅ Envoyé à {chat_id}")
        except Exception as e:
            print(f"❌ Erreur envoi Telegram : {e}")

def traiter_articles():
    """Cœur de l'usine : gère le flux de création."""
    print(f"\n🚀 Lancement du JT - {datetime.now().strftime('%H:%M')}")
    cache = set(json.load(open(CACHE_FILE)) if CACHE_FILE.exists() else [])
    
    nouveaux = [a for a in scraper_rss() if a['link'] not in cache]
    
    # --- LOGIQUE ANECDOTE SI VIDE ---
    if not nouveaux:
        print("💡 Pas d'actu aujourd'hui. Léa entre en scène pour une anecdote !")
        prompt_anecdote = "Tu es Léa, une experte passionnée d'impression 3D. Raconte une anecdote historique ou technique fascinante sur la 3D en 30 secondes. Sois dynamique et fun !"
        script = generer_script_ia(prompt_anecdote)
        
        # On crée un article fictif pour l'anecdote
        nouveaux = [{
            "source": "CULTURE 3D",
            "title": "Le saviez-vous ?",
            "link": "https://www.3dnatives.com",
            "summary": script,
            "is_anecdote": True
        }]
    
    print(f"📊 {len(nouveaux)} sujet(s) à traiter.")

    for article in nouveaux[:3]:
        try:
            # Choix de l'avatar : Léa pour les anecdotes, Angie pour les news
            if article.get("is_anecdote"):
                avatar = "lea_neutre.png"
                script = article['summary']
            else:
                avatar = "angie_neutre.png"
                prompt_news = f"Tu es Angie, présentatrice du JT 3D. Script de 30s pour : {article['title']}. Source: {article['source']}. Texte uniquement."
                script = generer_script_ia(prompt_news)
            
            article['script_jt'] = script
            chemin_avatar = str(IMAGES_DIR / avatar)
            
            # Vérification si l'image existe avant de lancer le montage
            if not os.path.exists(chemin_avatar):
                print(f"⚠️ Image {avatar} manquante dans /images. Utilisation d'un placeholder.")
                # Optionnel : tu peux mettre un chemin vers une image par défaut ici
            
            video = creer_video_article(article, chemin_avatar)
            
            if video and os.path.exists(video):
                envoyer_telegram(video, article)
                if not article.get("is_anecdote"):
                    cache.add(article['link'])
                    
        except Exception as e:
            print(f"❌ Erreur sur le sujet : {e}")

    # Mise à jour du cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(cache), f)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        traiter_articles()
    elif len(sys.argv) > 1 and sys.argv[1] == "schedule":
        heure = sys.argv[2] if len(sys.argv) > 2 else "20:00"
        schedule.every().day.at(heure).do(traiter_articles)
        print(f"⏰ Automate activé pour {heure}")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("Usage: python main.py [now|schedule HH:MM]")

if __name__ == "__main__":
    main()
