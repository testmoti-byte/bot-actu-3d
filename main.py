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
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Importer ton module d'animation
try:
    from video_animator import creer_video_article
except ImportError:
    print("⚠️ Module 'video_animator' non trouvé. Assure-toi qu'il est dans le même dossier.")

# Load env variables
load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
LISTE_ID = [id.strip() for id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if id.strip()]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configuration IA
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Chemins
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "videos"
CACHE_FILE = BASE_DIR / "articles_cache.json"

KEYWORDS_3D = [
    "impression 3d", "3d printing", "additive manufacturing", 
    "cao", "modélisation 3d", "résine", "fdm", "maker", "prototypage"
]

RSS_FEEDS = {
    "3dnatives": "https://www.3dnatives.com/fr/feed/",
    "fabbaloo": "https://www.fabbaloo.com/blog/feed.xml",
}

# ============ IA : GÉNÉRATION DU SCRIPT ============

def generer_script_jt(titre: str, resume: str) -> str:
    """Transforme un résumé d'article en script de présentatrice TV (Angie)."""
    prompt = f"""
    Tu es Angie, une présentatrice passionnée par l'impression 3D. 
    Réédite l'actualité suivante pour un JT court et dynamique de 30 secondes.
    Utilise un ton enthousiaste et professionnel. 
    
    TITRE: {titre}
    RÉSUMÉ: {resume}
    
    Format: Donne uniquement le texte que je dois lire, sans commentaires.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  ⚠️ Erreur Gemini: {e}")
        return f"Bonjour à tous ! Aujourd'hui on parle de : {titre}. Une avancée majeure pour le secteur."

# ============ SCRAPING & CACHE ============

def scraper_rss_feeds() -> List[Dict]:
    articles = []
    for source_name, rss_url in RSS_FEEDS.items():
        try:
            print(f"  📰 Scraping {source_name}...")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:10]:
                texte_complet = (entry.get('title', '') + " " + entry.get('summary', '')).lower()
                
                if any(kw in texte_complet for kw in KEYWORDS_3D):
                    # Tentative de récupération d'image dans le flux
                    image_url = None
                    if 'links' in entry:
                        for link in entry.links:
                            if 'image' in link.get('type', ''):
                                image_url = link.get('href')
                    
                    articles.append({
                        "source": source_name,
                        "title": entry.get('title', 'Sans titre'),
                        "link": entry.get('link', ''),
                        "summary": entry.get('summary', '')[:500],
                        "date": entry.get('published', datetime.now().isoformat()),
                        "image_url": image_url
                    })
        except Exception as e:
            print(f"  ❌ Erreur scraping {source_name}: {e}")
    return articles

def charger_cache() -> set:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def sauvegarder_cache(ids: set):
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(ids), f)

# ============ CORE LOGIC ============

def traiter_articles():
    print(f"\n🚀 DÉMARRAGE PIPELINE - {datetime.now().strftime('%H:%M:%S')}")
    
    cache = charger_cache()
    nouveaux = scraper_rss_feeds()
    
    a_traiter = [a for a in nouveaux if a['link'] not in cache]
    print(f"  📊 {len(a_traiter)} nouveaux articles à traiter.")

    for article in a_traiter[:3]: # Limite à 3 par cycle pour éviter les quotas
        try:
            print(f"\n🎬 Traitement: {article['title'][:50]}...")
            
            # 1. Générer le script avec Gemini
            script_jt = generer_script_jt(article['title'], article['summary'])
            article['script_jt'] = script_jt
            
            # 2. Appel au module d'animation
            # On passe le script généré au lieu du résumé brut
            angie_image = str(IMAGES_DIR / "angie_neutre.png")
            
            # Ici, j'assume que creer_video_article accepte le dictionnaire article
            video_path = creer_video_article(article, angie_image)
            
            if video_path and Path(video_path).exists():
                # 3. Diffusion
                diffuser_video_telegram(video_path, article)
                cache.add(article['link'])
            
        except Exception as e:
            print(f"  ❌ Erreur sur l'article: {e}")
            
    sauvegarder_cache(cache)
    print("\n✅ Cycle terminé")

def diffuser_video_telegram(video_path: str, article: Dict):
    for chat_id in LISTE_ID:
        try:
            message = (f"📺 *JT SPÉCIAL 3D*\n\n"
                       f"🎯 *{article['title']}*\n\n"
                       f"🔗 [Lire l'article]({article['link']})")
            
            with open(video_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                    data={'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'},
                    files={'video': v},
                    timeout=120
                )
            print(f"  ✅ Envoyé à {chat_id}")
        except Exception as e:
            print(f"  ❌ Erreur envoi Telegram ({chat_id}): {e}")

# ============ SCHEDULING & MAIN ============

def planifier(mode: str, valeur: str):
    if mode == "schedule":
        schedule.every().day.at(valeur).do(traiter_articles)
    elif mode == "every":
        schedule.every(int(valeur)).hours.do(traiter_articles)
    
    print(f"⏰ Mode {mode} activé ({valeur}). Ctrl+C pour quitter.")
    while True:
        schedule.run_pending()
        time.sleep(30)

def main():
    IMAGES_DIR.mkdir(exist_ok=True)
    VIDEOS_DIR.mkdir(exist_ok=True)

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "now":
            traiter_articles()
        elif mode in ["schedule", "every"]:
            valeur = sys.argv[2] if len(sys.argv) > 2 else ("20:00" if mode == "schedule" else "6")
            planifier(mode, valeur)
    else:
        print("Usage: python main.py [now|schedule HH:MM|every X]")

if __name__ == "__main__":
    main()
