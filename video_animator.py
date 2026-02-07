import os
import cv2
import numpy as np
from pathlib import Path
from moviepy.editor import (
    ImageClip, VideoFileClip, CompositeVideoClip, 
    TextClip, concatenate_videoclips
)
import google.generativeai as genai
from google.cloud import texttospeech
from typing import Optional, Tuple

# --- CONFIG ---
# (Les clés sont chargées via le main.py en général, mais on sécurise ici)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output/videos_generees"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ============ TRAITEMENT D'IMAGES ============

def extraire_chroma_key(image_path: str) -> np.ndarray:
    """Extrait le sujet (fond vert) et retourne une image RGBA."""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Impossible de charger {image_path}")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Plage verte optimisée
    lower_green = np.array([35, 45, 45])
    upper_green = np.array([85, 255, 255])
    
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.bitwise_not(mask)
    
    # Adoucir les bords du masque (anti-aliasing)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    img_rgba[:, :, 3] = mask
    return img_rgba

def creer_fond_studio() -> str:
    """Crée un fond pro si aucun n'est fourni."""
    fond = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)
    for i in range(VIDEO_HEIGHT):
        ratio = i / VIDEO_HEIGHT
        # Dégradé sombre pro (bleu nuit vers noir)
        fond[i, :] = [int(30 * (1-ratio)), int(15 * (1-ratio)), int(50 * (1-ratio))]
    
    path = str(TEMP_DIR / "fond_genere.png")
    cv2.imwrite(path, fond)
    return path

# ============ SYNTHÈSE VOCALE ============

def generer_audio(texte: str) -> Tuple[str, float]:
    """Génère l'audio et retourne (chemin, durée)."""
    output_path = str(TEMP_DIR / f"audio_{os.urandom(3).hex()}.mp3")
    
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=texte)
        
        # Voix féminine pro
        voice = texttospeech.VoiceSelectionParams(
            language_code="fr-FR",
            name="fr-FR-Neural2-A" # Version haute qualité si dispo
        )
        
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        # Utiliser moviepy pour obtenir la durée exacte de l'audio
        from moviepy.editor import AudioFileClip
        duration = AudioFileClip(output_path).duration
        return output_path, duration
        
    except Exception as e:
        print(f"⚠️ Erreur Google TTS: {e}. Fallback nécessaire.")
        # Ici tu pourrais mettre ton pyttsx3 si besoin
        return "", 0.0

# ============ COMPOSITION VIDÉO ============

def creer_video_article(article: dict, angie_image_path: str) -> Optional[str]:
    print(f"🎬 Création vidéo : {article['title']}")
    
    try:
        # 1. Script et Audio (On utilise le script généré par Gemini dans le main)
        script = article.get('script_jt', article['title'])
        audio_path, duree = generer_audio(script)
        
        if not audio_path: return None

        # 2. Préparation des éléments visuels
        # Angie
        angie_rgba = extraire_chroma_key(angie_image_path)
        angie_temp = str(TEMP_DIR / "angie_alpha.png")
        cv2.imwrite(angie_temp, angie_rgba)
        
        # Fond
        fond_path = creer_fond_studio()

        # 3. Montage MoviePy
        clips = []
        
        # Fond (ImageClip)
        fond_clip = ImageClip(fond_path).set_duration(duree).resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        clips.append(fond_clip)

        # Angie (Positionnée en bas au centre)
        angie_clip = ImageClip(angie_temp, transparent=True).set_duration(duree)
        angie_clip = angie_clip.resize(height=VIDEO_HEIGHT * 0.7) # Angie prend 70% de la hauteur
        angie_clip = angie_clip.set_position(('center', 'bottom'))
        clips.append(angie_clip)

        # Titre (TextClip) - Nécessite ImageMagick
        try:
            txt_clip = TextClip(
                article['title'].upper(),
                fontsize=70,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(VIDEO_WIDTH * 0.8, None),
                bg_color='rgba(0,0,0,0.5)' # Petit fond noir semi-transparent
            ).set_duration(duree).set_position(('center', 100))
            clips.append(txt_clip)
        except:
            print("⚠️ Erreur TextClip (ImageMagick?). Titre ignoré.")

        # Composition finale
        video = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        video.audio = AudioFileClip(audio_path)

        output_file = str(OUTPUT_DIR / f"JT_3D_{datetime.now().strftime('%H%M%S')}.mp4")
        
        video.write_videofile(output_file, fps=FPS, codec="libx264", audio_codec="aac", logger=None)
        
        # Nettoyage
        video.close()
        return output_file

    except Exception as e:
        print(f"❌ Erreur critique montage : {e}")
        return None
