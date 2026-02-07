import os
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips
from gtts import gTTS

def creer_video_article(article, chemin_avatar):
    """Gère le montage multi-couches : Intro -> [Ville + Bureau + Élise + Logo] + Voix"""
    
    # 1. Création de la voix (TTS)
    audio_path = "temp_audio.mp3"
    tts = gTTS(text=article['script_jt'], lang='fr')
    tts.save(audio_path)
    audio_clip = AudioFileClip(audio_path)
    duree = audio_clip.duration

    # 2. Préparation des couches visuelles (le "sandwich")
    # Fond : La ville S1
    ville = ImageClip("images/VILLE_S1.png").set_duration(duree).resize(height=1920)
    
    # Premier plan : Le rendu du bureau (avec ton fond vert)
    bureau = ImageClip("images/rendu_bureau.png").set_duration(duree).resize(height=1920)
    
    # Présentatrice : Élise
    presentatrice = (ImageClip(chemin_avatar)
                     .set_duration(duree)
                     .resize(width=850)
                     .set_position(("center", "bottom")))
    
    # Logo de la chaîne
    logo = (ImageClip("images/LOGO_CHAINE.png")
            .set_duration(duree)
            .resize(width=250)
            .set_position(("right", "top")))

    # 3. Assemblage du bloc JT
    # On empile : Ville (fond) < Bureau < Élise < Logo (dessus)
    clip_jt = CompositeVideoClip([ville, bureau, presentatrice, logo])
    clip_jt = clip_jt.set_audio(audio_clip)

    # 4. Ajout de l'Intro (COMMENCEMENT de Blender)
    chemin_intro = "VIDEO/COMMENCEMENT.blend0001-0063.mp4"
    if os.path.exists(chemin_intro):
        intro = VideoFileClip(chemin_intro)
        video_finale = concatenate_videoclips([intro, clip_jt])
    else:
        print(f"⚠️ Intro non trouvée à : {chemin_intro}")
        video_finale = clip_jt

    # 5. Exportation finale
    output_filename = "final_jt_production.mp4"
    video_finale.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Nettoyage
    audio_clip.close()
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return output_filename
