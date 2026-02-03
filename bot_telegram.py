import requests
import random
import google.generativeai as genai

# --- CONFIGURATION ---
TOKEN = "8547065074:AAEiZ4Jw5maZMbkYAIiJtnrIMPv1hk5dU54"
LISTE_ID = ["6773491313", "7776912126"]
GEMINI_API_KEY = "AIzaSyBqvv85GfwkdYnTHV-lMnOnCUXBm7ZJbBA"

# Configuration Gemini (Ton IA Studio)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def envoyer_video_telegram(message, video_url):
    for chat_id in LISTE_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
        # Gestion automatique des espaces dans le nom du fichier
        video_url_clean = video_url.replace(" ", "%20")
        
        payload = {
            "chat_id": chat_id,
            "video": video_url_clean,
            "caption": message,
            "parse_mode": "Markdown"
        }
        
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"✅ Succès ! Vidéo envoyée à {chat_id}")
        else:
            print(f"❌ Erreur {r.status_code} sur l'ID {chat_id} : {r.text}")

def compiler_jt_nj():
    # 1. NJ (Angy) crée son script de JT avec ta clé AI Studio
    prompt = "Tu es NJ (alias Angy), présentatrice du JT 3D de 20h. Ton style est fun et pro. Annonce en une phrase courte et percutante que le flash info commence."
    
    try:
        response = model.generate_content(prompt)
        script_nj = response.text.strip()
    except:
        script_nj = "Bonsoir David ! C'est NJ, voici l'actualité 3D en direct du studio !"

    # 2. On pointe vers la vidéo de NJ sur ton GitHub
    # Vérifie bien que le nom du fichier finit par .mp4 ou .mov
    video_nom = "NJ.mp4" # <--- Change ici si ton fichier s'appelle différemment sur GitHub
    video_url = f"https://raw.githubusercontent.com/testmoti-byte/bot-actu-3d/main/images/{video_nom}"
    
    # 3. Construction du message final
    message = f"📺 *JT DE 20H - ÉDITION SPÉCIALE*\n\n🎙️ *NJ :* {script_nj}\n\n🚀 #Impression3D #Actu"
    
    print(f"Tentative d'envoi de la vidéo : {video_nom}")
    envoyer_video_telegram(message, video_url)

if __name__ == "__main__":
    compiler_jt_nj()
