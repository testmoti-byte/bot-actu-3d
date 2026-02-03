import requests
import feedparser
import sys
import random
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

# --- STUDIO DES PRÉSENTATRICES (Noms exacts de tes fichiers GitHub) ---
EQUIPE = {
    "Léa": {
        "style": "passionnée, chaleureuse et dynamique",
        "matin": "LEA 2.png", 
        "soir": "LEA 1.png"
    },
    "Kate": {
        "style": "précise, geek et futuriste",
        "matin": "KATE 4.png", 
        "soir": "KATE 3.png"
    },
    "Angy": {
        "style": "créative, artistique et fun",
        "matin": "ANGY 1.png", 
        "soir": "ANGY 2.png"
    }
}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def envoyer_telegram(message, img_url):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        # On remplace les espaces par %20 pour que l'URL soit valide
        img_url_propre = img_url.replace(" ", "%20")
        payload = {"chat_id": chat_id, "photo": img_url_propre, "caption": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)

def compiler():
    nom_perso = random.choice(list(EQUIPE.keys()))
    img_nom = EQUIPE[nom_perso]["matin"]
    # Lien vers ton nouveau dossier /images/
    img_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{img_nom}"
    
    # Test sur Bambu Lab
    flux = feedparser.parse("https://blog.bambulab.com/feed/")
    if flux.entries:
        art = flux.entries[0]
        prompt = f"Tu es {nom_perso}. Résume en une phrase courte pour David : {art.title}"
        resume = model.generate_content(prompt).text.strip()
        
        message = f"🚀 *ACTU 3D : {nom_perso}*\n\n💬 {resume}\n🔗 [Lien]({art.link})"
        envoyer_telegram(message, img_url)

if __name__ == "__main__":
    compiler()
