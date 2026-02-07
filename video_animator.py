import os
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips

def creer_video_article(article, chemin_avatar):
    # 1. Audio
    audio_path = "temp_audio.mp3"
    # (Garde ta partie gTTS ici)
    audio_clip = AudioFileClip(audio_path)
    duree = audio_clip.duration

    # 2. On définit une taille standard (ex: Format Portrait TikTok/Reels)
    TAILLE_FINALE = (1080, 1920)

    # 3. Préparation des couches avec redimensionnement forcé
    ville = ImageClip("images/VILLE_S1.png").set_duration(duree).resize(TAILLE_FINALE)
    bureau = ImageClip("images/rendu_bureau.png").set_duration(duree).resize(TAILLE_FINALE)
    
    presentatrice = (ImageClip(chemin_avatar)
                     .set_duration(duree)
                     .resize(width=900)
                     .set_position(("center", "bottom")))

    # 4. Montage du bloc News
    clip_jt = CompositeVideoClip([ville, bureau, presentatrice], size=TAILLE_FINALE).set_audio(audio_clip)

    # 5. Chargement de l'Intro avec mise en conformité
    chemin_intro = "VIDEO/COMMENCEMENT.blend0001-0063.mp4"
    if os.path.exists(chemin_intro):
        intro = VideoFileClip(chemin_intro).resize(TAILLE_FINALE).set_fps(24)
        video_finale = concatenate_videoclips([intro, clip_jt], method="compose") # "compose" aide à éviter les glitchs
    else:
        video_finale = clip_jt

    # 6. Export avec réglages de compatibilité
    output_filename = "final_jt_production.mp4"
    video_finale.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        temp_audiofile='temp-audio.m4a', 
        remove_temp=True
    )
    
    return output_filename
