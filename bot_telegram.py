import requests
import feedparser
import sys
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

# Configuration de l'IA Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SOURCES_NEWS = [
    "https://blog.bambulab.com/feed/",
    "https://www.creality.com/blog/rss",
    "https://3dprint.com/feed/",
    "https://all3dp.com/feed/",
    "https://www.3dnatives.com/feed/",
    "https://blog.prusa3d.com/feed/",
    "https://www.voxelmatters.com/feed/",
    "https://www.seeedstudio.com/blog/feed/",
    "https://3dtoday.ru/news/rss",
    "https://www.materialise.com/en/blog/rss",
    "https://cults3d.com/fr/flux-de-conception.rss",
    "https://www.thingiverse.com/rss/newest",
    "https://hackaday.com/blog/category/3d-printing/feed/",
    "https://www.instructables.com/rss/workshop/",
    "https://www.hackster.io/feed",
    "https://www.tomshardware.com/rss/3d-printing"
]

SOURCES_YOUTUBE = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCidjtV8Lid-7unVogZunfBw", # Heliox
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4vE8_XqS8SAtF_pGue7p_w", # Frères Poulain
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-VfW_C9G_C-fI8vUfCcl3w", # LesImprimantes3D
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC_7aK9qzG95xeVXYY9Wf0fQ", # 3D Printing Nerd
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC6f-C7_m9Z8L_F_286GAt9Q", # Dmitry Sorkin
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCiczXOhuGQTn7IDuScwQbFA", # CNC Kitchen
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvK6pS_85Z_YmY0X9_uX5Sg", # Le GüeroLoco
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCf8_mSotV89vYID7T9S6W_g", # Punished Props
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-3I5_M6K_u-mP4n_D7_WwA", # Frankly Built
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC7vVhkEfw4nOGp8TyDk7vqw", # James Bruton
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCVc6AHfGwClf_S686H87_Zw", # Make Anything
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC5Lbnd97xsY-W3Xy7nMFIDg", # Uncle Jessy
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCtnGthnw9ps86S96s9D6nsw", # Teaching Tech
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCy_9v-nL8m0V4C9f_46mR_g", # 3D Print Academy
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCpOlOeQjj7EsVnDh3zuCgsA", # Adafruit
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCP5e2SYUXpx_mH1M_15E39w", # Real Engineering
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCbv2mDrNJne8Z_v_6TzS3XQ"  # 3D Printing Pro
]

def generer_resume_lea(titre_article):
    prompt = f"""Tu es Léa, une experte en impression 3D et personnage de BD. 
    Résume cet article en une phrase courte et dynamique pour David. 
    Sois sympa et passionnée. Article : {titre_article}"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Hé David ! J'ai déniché ça pour toi : {titre_article}"

def envoyer_telegram(message):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown", "disable_web_page_preview": True}
        requests.post(url, data=payload)

def compiler(urls, titre_journal):
    message_final = f"🤖 *{titre_journal}*\n━━━━━━━━━━━━━━━\n\n"
    il_y_a_24h = datetime.now() - timedelta(hours=24)
    trouve = False
    
    for url in urls:
        try:
            flux = feedparser.parse(url)
            nom_source = flux.feed.title.replace(" - YouTube", "") if 'title' in flux.feed else "Source"
            for art in flux.entries[:1]: # On prend le dernier de chaque source
                date = art.get('published_parsed') or art.get('updated_parsed')
                if date and datetime(*date[:6]) > il_y_a_24h:
                    resume = generer_resume_lea(art.title)
                    message_final += f"📍 *{nom_source}*\n💬 {resume}\n🔗 [Lien]({art.link})\n\n"
                    trouve = True
        except: continue
        
    if trouve:
        envoyer_telegram(message_final)
    else:
        envoyer_telegram(f"☕ Rien de neuf sous le soleil de la 3D ce coup-ci, David !")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "matin"
    if mode == "matin":
        compiler(SOURCES_NEWS, "LE BRIEF DE LÉA ☀️")
    else:
        compiler(SOURCES_YOUTUBE, "LA VEILLE VIDÉO DE LÉA 🌙")
