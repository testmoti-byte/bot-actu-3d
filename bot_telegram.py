import requests
import random
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- STUDIO JT ---
# Ici, on remplace les .png par des fichiers .mp4 (tes animations)
EQUIPE_JT = {
    "Léa": {
        "video": "LEA_JT_ROBE_NOIRE.mp4",
        "intro": "Bonsoir David, voici les titres de l'actualité 3D."
    }
}

def envoyer_video_telegram(message, video_url):
    for chat_id in LISTE_ID:
        # On utilise sendVideo au lieu de sendPhoto
        url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
        payload = {
            "chat_id": chat_id,
            "video": video_url,
            "caption": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)

def compiler_jt():
    # 1. On demande à l'IA de faire un script style JT
    prompt = "Écris une seule phrase style présentatrice de JT de 20h pour annoncer une nouveauté sur l'impression 3D."
    res = model.generate_content(prompt).text.strip()
    
    # 2. On pointe vers ta vidéo animée sur ton GitHub
    # Tu devras mettre ton fichier .mp4 dans le dossier /images
    video_nom = EQUIPE_JT["Léa"]["video"]
    video_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{video_nom}"
    
    # 3. Envoi
    message = f"📺 *ÉDITION SPÉCIALE*\n\n{res}"
    envoyer_video_telegram(message, video_url)

if __name__ == "__main__":
    compiler_jt()
