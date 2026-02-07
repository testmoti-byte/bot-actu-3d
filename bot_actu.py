import os
import sys
import json
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv

# --- CHARGEMENT CONFIG ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
LISTE_ID = [id.strip() for id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if id.strip()]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialisation IA
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

BASE_DIR = Path(__file__).parent
CACHE_FILE = BASE_DIR / "articles_vus.json"

# ============ SOURCES MONDIALES (NETTOYÉES) ============
RSS_FEEDS = {
    "Bambu Lab": "https://blog.bambulab.com/feed/",
    "Hackaday": "https://hackaday.com/blog/category/3d-printing/feed/",
    "Creality": "https://www.creality.com/blog/rss",
    "3DPrint.com": "https://3dprint.com/feed/",
    "All3DP": "https://all3dp.com/feed/",
    "3DNatives": "https://www.3dnatives.com/feed/",
    "Prusa": "https://blog.prusa3d.com/feed/",
    "VoxelMatters": "https://www.voxelmatters.com/feed/",
    "Seeed Studio": "https://www.seeedstudio.com/blog/feed/",
    "3DToday (RU)": "https://3dtoday.ru/news/rss",
    "Materialise": "https://www.materialise.com/en/blog/rss",
    "Cults3D": "https://cults3d.com/fr/flux-de-conception.rss",
    "Thingiverse": "https://www.thingiverse.com/rss/newest",
    "Instructables": "https://www.instructables.com/rss/workshop/",
    "Hackster": "https://www.hackster.io/feed",
    "Tom's Hardware": "https://www.tomshardware.com/rss/3d-printing",
    "Heliox": "https://www.youtube.com/feeds/videos.xml?channel_id=UCidjtV8Lid-7unVogZunfBw",
    "LesImprimantes3D": "https://www.youtube.com/feeds/videos.xml?channel_id=UC-VfW_C9G_C-fI8vUfCcl3w",
    "Dmitry Sorkin": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6f-C7_m9Z8L_F_286GAt9Q",
    "Le GüeroLoco": "https://www.youtube.com/feeds/videos.xml?channel_id=UCvK6pS_85Z_YmY0X9_uX5Sg",
    "Punished Props": "https://www.youtube.com/feeds/videos.xml?channel_id=UCf8_mSotV89vYID7T9S6W_g",
    "Frankly Built": "https://www.youtube.com/feeds/videos.xml?channel_id=UC-3I5_M6K_u-mP4n_D7_WwA",
    "James Bruton": "https://www.youtube.com/feeds/videos.xml?channel_id=UC7vVhkEfw4nOGp8TyDk7vqw",
    "Make Anything": "https://www.youtube.com/feeds/videos.xml?channel_id=UCVc6AHfGwClf_S686H87_Zw",
    "Uncle Jessy": "https://www.youtube.com/feeds/videos.xml?channel_id=UC5Lbnd97xsY-W3Xy7nMFIDg",
    "Teaching Tech": "https://www.youtube.com/feeds/videos.xml?channel_id=UCtnGthnw9ps86S96s9D6nsw",
    "3D Print Academy": "https://www.youtube.com/feeds/videos.xml?channel_id=UCy_9v-nL8m0V4C9f_46mR_g",
    "Adafruit": "https://www.youtube.com/feeds/videos.xml?channel_id=UCpOlOeQjj7EsVnDh3zuCgsA",
    "Real Engineering": "https://www.youtube.com/feeds/videos.xml?channel_id=UCP5e2SYUXpx_mH1M_15E39w",
    "3D Printing Pro": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbv2mDrNJne8Z_v_6TzS3XQ",
    "Frères Poulain": "https://www.youtube.com/feeds/videos.xml?channel_id=UC4vE8_XqS8SAtF_pGue7p_w",
    "CNC Kitchen": "https://www.youtube.com/feeds/videos.xml?channel_id=UCiczXOhuGQTn7IDuScwQbFA",
    "3D Printing Nerd": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_7aK9qzG95xeVXYY9Wf0fQ"
}

KEYWORDS = ["3d", "printing", "impression", "imprimante", "fdm", "résine", "resin", "sla", "klipper", "voron", "bambu", "creality"]

# ============ LOGIQUE IA ============
def generer_script_jt(article: Dict) -> str:
    prompt = f"""
    Rédige un script de JT (45 sec) court et dynamique.
    INFO : {article['title']}
    SOURCE : {article['source']}
    RÉSUMÉ : {article['summary']}

    PERSONNAGES ET PERSONNALITÉS :
    - KATE (Bretonne, chef, directe, cherche le scoop, autoritaire).
    - ANGIE (Belge, bienveillante, calme, vérifie l'humain).
    - LEA (Marseillaise, gaffeuse, enthousiaste, créative).
    - ELISE (Québécoise, geek, méticuleuse, gère la tech et la traduction).

    CONSIGNES :
    1. Élise traduit avec son accent si la source est étrangère.
    2. Kate lance le scoop avec énergie.
    3. Léa finit par une boulette et demande aux abonnés TikTok de partager leurs prints en commentaire pour être mis en lumière !
    4. Format : Nom du perso : [Texte]
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Kate : On a un souci technique, mais l'info est là : {article['title']}"

# ============ SCRAPER ============
def scraper_articles() -> List[Dict]:
    articles = []
    print(f"📡 Scan de {len(RSS_FEEDS)} sources mondiales...")
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                if any(k in (title + summary).lower() for k in KEYWORDS):
                    articles.append({
                        "source": name,
                        "title": title,
                        "link": entry.get('link', ''),
                        "summary": summary[:500],
                        "date": entry.get('published', '')
                    })
        except:
            continue
    return articles

def charger_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f: return set(json.load(f))
    return set()

def sauvegarder_cache(cache):
    with open(CACHE_FILE, 'w') as f: json.dump(list(cache), f)

# ============ DIFFUSION ============
def envoyer_telegram(article: Dict, script: str):
    for chat_id in LISTE_ID:
        try:
            message = (f"📺 *JT IMPRESSION 3D - LE QUATUOR*\n\n"
                       f"{script}\n\n"
                       f"🔗 [Source : {article['source']}]({article['link']})\n"
                       f"🌍 _Script généré par l'équipe rédactionnelle_")
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'})
        except Exception as e:
            print(f"❌ Erreur envoi: {e}")

# ============ EXECUTION ============
def executer_jt():
    cache = charger_cache()
    articles = scraper_articles()
    nouveaux = [a for a in articles if a['link'] not in cache]
    
    print(f"📊 {len(nouveaux)} nouvelles infos trouvées.")
    for article in nouveaux[:3]:
        print(f"✨ Scripting : {article['title'][:40]}...")
        script = generer_script_jt(article)
        envoyer_telegram(article, script)
        cache.add(article['link'])
        
    sauvegarder_cache(cache)
    print("✅ JT Terminé.")

if __name__ == "__main__":
    executer_jt()
