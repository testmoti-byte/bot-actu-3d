import os
import cv2
import numpy as np
from pathlib import Path
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip

# --- CONFIG ---
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 24

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def generer_video_animateur(texte, avatar_path, output_path):
    """Version simplifiée pour valider le test GitHub"""
    print(f"🎬 Création vidéo pour l'avatar : {avatar_path}")
    
    try:
        if not os.path.exists(avatar_path):
            print(f"⚠️ Image manquante : {avatar_path}")
            return False

        # 1. Création d'un fond simple (Bleu nuit)
        fond = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)
        fond[:] = [50, 15, 30] # BGR
        fond_path = "temp_fond.png"
        cv2.imwrite(fond_path, fond)

        # 2. Montage MoviePy simple
        duree = 5 # Vidéo de 5 secondes pour le test
        
        fond_clip = ImageClip(fond_path).set_duration(duree)
        avatar_clip = ImageClip(avatar_path).set_duration(duree).resize(width=VIDEO_WIDTH*0.8)
        avatar_clip = avatar_clip.set_position(('center', 'bottom'))

        video = CompositeVideoClip([fond_clip, avatar_clip], size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        
        # On génère sans audio pour le premier test car Google Cloud TTS demande une config complexe
        video.write_videofile(output_path, fps=FPS, codec="libx264", logger=None)
        
        video.close()
        return True

    except Exception as e:
        print(f"❌ Erreur montage : {e}")
        return False
