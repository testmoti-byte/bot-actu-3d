import requests
import feedparser
import sys
import random
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

# --- STUDIO DES PRÉSENTATRICES ---
# Note : Assure-toi que tes fichiers dans le dossier /images s'appellent exactement comme ça
EQUIPE = {
    "Léa": {
        "style": "passionnée, chaleureuse et dynamique",
        "matin": "LEA_2.png",
        "soir": "LEA_1.png"
    },
    "Kate": {
        "style": "précise, geek et futuriste",
        "matin": "KATE_4.png",
        "soir": "KATE_3.png"
    },
    "Angy": {
        "style": "créative, artistique et fun",
        "matin": "ANGY_1.png",
        "soir": "ANGY_2.png"
    }
}

# Configuration de l'IA Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SOURCES ---
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

def generer_resume_ia(titre_article, nom_perso):
    style = EQUIPE[nom_perso]["style"]
    prompt = f"Tu es {nom_perso}, experte en impression 3D. Ton style est {style}. Résume cet article en une phrase courte et sympa pour David : {titre_article}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Hey David ! J'ai trouvé ça pour toi : {titre_article}"

def envoyer_telegram(message, img_url):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": img_url,
            "caption": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        requests.post(url, data=payload)

def compiler(urls, titre_journal, mode):
    # Choisir la présentatrice et son image
    nom_perso = random.choice(list(EQUIPE.keys()))
    img_nom = EQUIPE[nom_perso][mode]
    img_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{img_nom}"
    
    message_final = f"🤖 *{titre_journal} par {nom_perso}*\n━━━━━━━━━━━━━━━\n\n"
    il_y_a_24h = datetime.now() - timedelta(hours=24)
    trouve = False
    
    for url in urls:
        try:
            flux = feedparser.parse(url)
            for art in flux.entries[:1]:
                # On simplifie la vérification de date pour le test
                resume = generer_resume_ia(art.title, nom_perso)
                message_final += f"📍 *{nom_perso}* : {resume}\n🔗 [Lien]({art.link})\n\n"
                trouve = True
        except: continue
        
    if trouve:
        envoyer_telegram(message_final, img_url)
    else:
        envoyer_telegram(f"☕ Rien de neuf aujourd'hui David ! - {nom_perso}", img_url)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "matin"
    if mode == "matin":
        compiler(SOURCES_NEWS, "LE BRIEF DE L'ACTU ☀️", "matin")
    else:
        compiler(SOURCES_YOUTUBE, "LA VEILLE VIDÉO 🌙", "soir")
