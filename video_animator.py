import os
import cv2
import numpy as np
from pathlib import Path
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip
# On retire TextClip qui fait planter GitHub

OUTPUT_DIR = Path("videos")
OUTPUT_DIR.mkdir(exist_ok=True)

def extraire_chroma_key(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None: return None
    # Si l'image n'a pas d'alpha, on en crée un
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img

def creer_video_article(article: dict, angie_path: str) -> str:
    output_path = OUTPUT_DIR / f"news_{hash(article['title']) % 1000}.mp4"
    duree = 5.0 # Durée fixe pour le test GitHub
    
    try:
        # 1. Fond dégradé OpenCV
        fond = np.zeros((1920, 1080, 3), dtype=np.uint8)
        fond[:, :] = [100, 50, 0] # Bleu foncé
        
        # 2. Ajout du titre directement sur l'image (Remplace TextClip)
        cv2.putText(fond, article['title'][:30], (50, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        fond_path = "/tmp/fond_temp.png"
        cv2.imwrite(fond_path, fond)

        # 3. Traitement Angie
        angie_rgba = extraire_chroma_key(angie_path)
        angie_temp = "/tmp/angie_temp.png"
        if angie_rgba is not None:
            angie_resized = cv2.resize(angie_rgba, (800, 1200))
            cv2.imwrite(angie_temp, angie_resized)
        
        # 4. Composition MoviePy simplifiée
        fond_clip = ImageClip(fond_path).set_duration(duree)
        clips = [fond_clip]
        
        if os.path.exists(angie_temp):
            angie_clip = ImageClip(angie_temp, transparent=True).set_duration(duree).set_position(("center", "bottom"))
            clips.append(angie_clip)

        video = CompositeVideoClip(clips, size=(1080, 1920))
        video.write_videofile(str(output_path), fps=24, codec="libx264", logger=None)
        
        return str(output_path)
    except Exception as e:
        print(f"❌ Erreur video_animator : {e}")
        return None
