import os
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips
from gtts import gTTS
from pathlib import Path

def creer_video_article(article, chemin_avatar):
    # 1. Génération de la voix
    audio_path = "temp_audio.mp3"
    tts = gTTS(text=article['script_jt'], lang='fr')
    tts.save(audio_path)
    audio_clip = AudioFileClip(audio_path)
    duree = audio_clip.duration

    # 2. Chargement des images (Fond, Bureau, Logo)
    # Note : MoviePy peut supprimer le fond vert avec .mask_color
    ville = ImageClip("images/VILLE_S1.png").set_duration(duree).resize(height=1080)
    bureau = ImageClip("images/rendu_bureau.png").set_duration(duree).resize(height=1080)
    # Ici, on simule l'incrustation. Si ton rendu bureau a un vrai fond vert :
    # bureau = bureau.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)

    logo = (ImageClip("images/LOGO_CHAINE.png")
            .set_duration(duree)
            .resize(width=200)
            .set_position(("right", "top")))

    presentatrice = (ImageClip(chemin_avatar)
                     .set_duration(duree)
                     .resize(height=800)
                     .set_position(("center", "bottom")))

    # 3. Montage du JT (Le Sandwich)
    # Ordre : Ville -> Bureau -> Présentatrice -> Logo
    clip_jt = CompositeVideoClip([ville, bureau, presentatrice, logo])
    clip_jt = clip_jt.set_audio(audio_clip)

    # 4. Ajout de l'Intro Blender
    chemin_intro = "VIDEO/COMMENCEMENT.blend0001-0063.mp4"
    if os.path.exists(chemin_intro):
        intro = VideoFileClip(chemin_intro)
        video_finale = concatenate_videoclips([intro, clip_jt])
    else:
        video_finale = clip_jt

    # 5. Export
    output_filename = f"JT_Elise_{int(os.getpid())}.mp4"
    video_finale.write_videofile(output_filename, fps=24, codec="libx264")
    
    return output_filename
