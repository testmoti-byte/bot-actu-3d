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

# Import du module vidéo (doit être dans le même dossier sur GitHub)
try:
    from video_animator import creer_video_article
except ImportError:
    print("⚠️ Module 'video_animator' non trouvé. Assure-toi qu'il est présent sur ton GitHub.")

# Chargement des variables d'environnement
load_dotenv()

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
LISTE_ID = [id.strip() for id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if id.strip()]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configuration de l'IA Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Chemins et Dossiers
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
VIDEOS_DIR = BASE_DIR / "videos"
CACHE_FILE = BASE_DIR / "articles_cache.json"

# Création des dossiers si inexistants
IMAGES_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Mots-clés pour le filtrage
KEYWORDS_3D = [
    "impression 3d", "3d printing", "additive manufacturing", 
    "cao", "modélisation 3d", "résine", "fdm", "maker", "prototypage"
]

# TES SOURCES SONT ICI : Ajoute tes nouveaux liens ici
RSS_FEEDS = {
    "3dnatives": "https://www.3dnatives.com/fr/feed/",
    "fabbaloo": "https://www.fabbaloo.com/blog/feed.xml",
}

# ============ IA : TRADUCTION ET SCRIPT ============

def generer_script_jt(titre: str, resume: str, source_name: str) -> str:
    """Traduit et adapte l'article pour le JT d'Angie."""
    prompt = f"""
    Tu es Angie, présentatrice passionnée d'un JT sur l'impression 3D.
    
    INFO À TRAITER :
    SOURCE: {source_name}
    TITRE: {titre}
    RÉSUMÉ: {resume}
    
    MISSION :
    1. Si l'info est en anglais, traduis-la en français de manière fluide.
    2. Réécris le texte pour un JT dynamique de 30 secondes.
    3. Ton ton doit être enthousiaste et professionnel.
    4. Donne UNIQUEMENT le texte à lire, sans commentaires.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  ⚠️ Erreur Gemini: {e}")
        return f"Bonjour à tous ! Aujourd'hui, {source_name} nous rapporte : {titre}. Une info cruciale pour le secteur."

# ============ SCRAPING & GESTION CACHE ============

def scraper_rss_feeds() -> List[Dict]:
    articles = []
    for source_name, rss_url in RSS_FEEDS.items():
        try:
            print(f"  📰 Scraping {source_name}...")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:10]:
                texte_complet = (entry.get('title', '') + " " + entry.get('summary', '')).lower()
                
                if any(kw in texte_complet for kw in KEYWORDS_3D):
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

# ============ DIFFUSION TELEGRAM ============

def diffuser_video_telegram(video_path: str, article: Dict):
    """Envoie la vidéo finale avec la source et le lien."""
    for chat_id in LISTE_ID:
        try:
            message = (
                f"📺 *JT SPÉCIAL 3D BY ANGIE*\n\n"
                f"🎯 *{article['title']}*\n\n"
                f"📍 *Source :* {article['source'].upper()}\n"
                def creer_video_article(article: dict, angie_image_path: str) -> Optional[str]:
                f"🤖 _Traduction et synthèse par Gemini 1.5 Flash_"
            )
            
            with open(video_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                    data={'chat_id': chat_id, 'caption': message, 'parse_mode': 'Markdown'},
                    files={'video': v},
                    timeout=150
                )
            print(f"  ✅ Envoyé avec succès à {chat_id}")
        except Exception as e:
            print(f"  ❌ Erreur envoi Telegram ({chat_id}): {e}")

# ============ LOGIQUE PRINCIPALE ============

def traiter_articles():
    print(f"\n🚀 DÉMARRAGE DU JT - {datetime.now().strftime('%H:%M:%S')}")
    
    cache = charger_cache()
    nouveaux = scraper_rss_feeds()
    
    a_traiter = [a for a in nouveaux if a['link'] not in cache]
    print(f"  📊 {len(a_traiter)} nouveaux articles détectés.")

    for article in a_traiter[:3]: # Limite à 3 pour ne pas saturer
        try:
            print(f"\n🎬 Préparation : {article['title'][:50]}...")
            
            # Génération du script traduit
            script_jt = generer_script_jt(article['title'], article['summary'], article['source'])
            article['script_jt'] = script_jt
            
            # Chemin vers l'image d'Angie (à mettre dans ton dossier /images sur GitHub)
            angie_path = str(IMAGES_DIR / "angie_neutre.png")
            
            # Création de la vidéo via le module vidéo_animator
            video_path = creer_video_article(article, angie_path)
            
            if video_path and Path(video_path).exists():
                diffuser_video_telegram(video_path, article)
                cache.add(article['link'])
            
        except Exception as e:
            print(f"  ❌ Échec du traitement : {e}")
            
    sauvegarder_cache(cache)
    print("\n✅ Session terminée.")

# ============ LANCEMENT ============

def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "now":
            traiter_articles()
        elif mode == "schedule":
            valeur = sys.argv[2] if len(sys.argv) > 2 else "18:00"
            schedule.every().day.at(valeur).do(traiter_articles)
            print(f"⏰ JT planifié tous les jours à {valeur}.")
            while True:
                schedule.run_pending()
                time.sleep(60)
    else:
        print("Usage: python main.py [now|schedule HH:MM]")

if __name__ == "__main__":
    main()

