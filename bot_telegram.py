import requests
import feedparser
import sys
import random
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
# Liste d'IDs : on va forcer l'envoi sur les deux pour être sûr
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

# --- STUDIO DES PRÉSENTATRICES ---
# ATTENTION : Les noms ici doivent être EXACTEMENT comme sur GitHub
EQUIPE = {
    "Léa": {"style": "passionnée", "matin": "LEA_2.png", "soir": "LEA_1.png"},
    "Kate": {"style": "geek", "matin": "KATE_4.png", "soir": "KATE_3.png"},
    "Angy": {"style": "fun", "matin": "ANGY_2.png", "soir": "ANGY_1.png"}
}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def envoyer_telegram(message, img_url):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": img_url, "caption": message, "parse_mode": "Markdown"}
        r = requests.post(url, data=payload)
        print(f"Envoi ID {chat_id} | Code: {r.status_code} | Réponse: {r.text}")

def compiler():
    nom_perso = random.choice(list(EQUIPE.keys()))
    img_nom = EQUIPE[nom_perso]["matin"]
    # LIEN CORRIGÉ : On pointe directement à la racine du projet
    img_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/{img_nom}"
    
    flux = feedparser.parse("https://blog.bambulab.com/feed/")
    if flux.entries:
        art = flux.entries[0]
        prompt = f"Tu es {nom_perso}. Résume en une phrase courte pour David : {art.title}"
        resume = model.generate_content(prompt).text.strip()
        
        message = f"🚀 *TEST FINAL*\n\nPrésentatrice : {nom_perso}\n💬 {resume}\n🔗 [Lien]({art.link})"
        envoyer_telegram(message, img_url)

if __name__ == "__main__":
    compiler()
