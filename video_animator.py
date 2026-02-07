import os
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip
from gtts import gTTS
from pathlib import Path

def creer_video_article(article, chemin_avatar):
    """Crée une vidéo complète avec voix, fond et personnage."""
    
    # 1. Générer l'audio à partir du script Gemini
    audio_path = "temp_audio.mp3"
    tts = gTTS(text=article['script_jt'], lang='fr')
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    duree = audio_clip.duration

    # 2. Création du Fond (Couleur ou Image de studio)
    # On crée un fond bleu de 1080x1920 (format TikTok/Reels)
    fond = ColorClip(size=(1080, 1920), color=[0, 51, 102]).set_duration(duree)

    # 3. Ajout de la présentatrice (Léa ou Angie)
    # On la place en bas de l'écran
    presentatrice = (ImageClip(chemin_avatar)
                     .set_duration(duree)
                     .resize(width=900) # Ajuste selon tes images
                     .set_position(("center", "bottom")))

    # 4. Ajout du Titre
    from moviepy.editor import TextClip
    # Note: TextClip peut être capricieux sur GitHub, on commence simple
    
    # Assemblage final
    video = CompositeVideoClip([fond, presentatrice])
    video = video.set_audio(audio_clip)

    # Exportation
    output_filename = f"video_{int(os.getpid())}.mp4"
    video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Nettoyage
    audio_clip.close()
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return output_filename
