import requests
import random
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def envoyer_telegram(message, media_url):
    for chat_id in LISTE_ID:
        # Comme ton fichier finit par .png, on utilise sendPhoto
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        media_url_clean = media_url.replace(" ", "%20")
        
        payload = {
            "chat_id": chat_id,
            "photo": media_url_clean,
            "caption": message,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, data=payload)
        print(f"Statut envoi : {r.status_code}")

def compiler_jt():
    prompt = "Tu es NJ, présentatrice vedette du JT de 20h. Annonce le début du flash info 3D avec élégance."
    try:
        res = model.generate_content(prompt).text.strip()
    except:
        res = "Bonsoir David, voici l'édition spéciale du JT 3D !"

    # --- CORRECTION DU NOM ICI ---
    # On utilise le nom EXACT que je vois sur ta photo GitHub
    image_nom = "ANGY_JT_ROBE_NOIRE.mp4.png" 
    url_finale = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{image_nom}"
    
    message = f"📺 *JT DE 20H - NJ EN DIRECT*\n\n🎙️ {res}"
    envoyer_telegram(message, url_finale)

if __name__ == "__main__":
    compiler_jt()
