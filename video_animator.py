import os
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips

def creer_video_article(article, chemin_avatar):
    # 1. Audio (TTS)
    audio_path = "temp_audio.mp3"
    # ... (ton code gTTS habituel)
    audio_clip = AudioFileClip(audio_path)
    duree = audio_clip.duration

    # 2. On s'aligne sur tes réglages Blender
    RESOLUTION = (1080, 1920)
    FPS_CIBLE = 30 # On passe de 24 à 30 ici

    # 3. Préparation des couches
    ville = ImageClip("images/VILLE_S1.png").set_duration(duree).resize(RESOLUTION)
    bureau = ImageClip("images/rendu_bureau.png").set_duration(duree).resize(RESOLUTION)
    
    presentatrice = (ImageClip(chemin_avatar)
                     .set_duration(duree)
                     .resize(width=900)
                     .set_position(("center", "bottom")))

    # 4. Montage News
    clip_jt = CompositeVideoClip([ville, bureau, presentatrice], size=RESOLUTION).set_audio(audio_clip)

    # 5. Intro (Ton rendu Blender 30 FPS)
    chemin_intro = "VIDEO/COMMENCEMENT.blend0001-0063.mp4"
    if os.path.exists(chemin_intro):
        # On force MoviePy à lire ton intro à 30 FPS sans la déformer
        intro = VideoFileClip(chemin_intro).resize(RESOLUTION).set_fps(FPS_CIBLE)
        # "method='compose'" est crucial pour éviter que les deux clips se "battent"
        video_finale = concatenate_videoclips([intro, clip_jt], method="compose")
    else:
        video_finale = clip_jt

    # 6. Exportation haute compatibilité
    output_filename = "final_jt_production.mp4"
    video_finale.write_videofile(
        output_filename, 
        fps=FPS_CIBLE, 
        codec="libx264", 
        preset="ultrafast", # Accélère le rendu sur GitHub
        audio_codec="aac"
    )
    
    return output_filename
