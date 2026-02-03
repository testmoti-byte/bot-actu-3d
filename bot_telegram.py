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

# --- CONFIGURATION IA ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SOURCES TEST (On force une source qui marche) ---
SOURCES_TEST = ["https://blog.bambulab.com/feed/"]

def generer_resume_ia(titre_article, nom_perso):
    style = EQUIPE[nom_perso]["style"]
    prompt = f"Tu es {nom_perso}, experte 3D. Ton style est {style}. Résume en une phrase fun pour David : {titre_article}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Hey David ! Regarde cette actu : {titre_article}"

def envoyer_telegram(message, img_url):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": chat_id, 
            "photo": img_url, 
            "caption": message, 
            "parse_mode": "Markdown"
        }
        r = requests.post(url, data=payload)
        print(f"Envoi à {chat_id} | Statut: {r.status_code}")

def compiler(urls, titre_journal, mode):
    nom_perso = random.choice(list(EQUIPE.keys()))
    img_nom = EQUIPE[nom_perso][mode]
    img_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{img_nom}"
    
    print(f"Lancement du test avec {nom_perso}...")
    
    for url in urls:
        flux = feedparser.parse(url)
        if flux.entries:
            art = flux.entries[0]
            resume = generer_resume_ia(art.title, nom_perso)
            message = f"🚀 *TEST STUDIO ACTU*\n\nPrésentatrice : *{nom_perso}*\n💬 {resume}\n🔗 [Voir l'article]({art.link})"
            envoyer_telegram(message, img_url)
            return # On envoie juste un message pour valider le test

if __name__ == "__main__":
    # On lance le test forcé
    compiler(SOURCES_TEST, "TEST", "matin")
