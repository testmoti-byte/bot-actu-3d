#!/usr/bin/env python3
"""
Blender Script - S'exécute DANS Blender
Ce script est appelé par blender_oracle.py

Fonctionnalités :
- Importe Kara dans le studio
- Charge les animations Mixamo
- Synchronise avec l'audio
- Gère les caméras (zoom 0-2s puis plan fixe)
- Lance le rendu vidéo
"""

import bpy
import os
import sys
import json
from math import floor

# ============================================================
# CONFIGURATION - Récupère les paramètres de blender_oracle.py
# ============================================================

# Lire les variables d'environnement passées par blender_oracle.py
_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

# Chemins (relatifs au fichier .blend)
CONFIG = {
    # Fichiers
    "kara_fbx": "animations/Kara.fbx",  # Chemin vers Kara en FBX
    
    # Animations Mixamo (dans le dossier animations/)
    "animations": {
        "sitting_drinking": "animations/Sitting Drinking.fbx",
        "sitting_talking": "animations/Sitting Talking.fbx",
        "stand_to_sit": "animations/Stand To Sit.fbx",
        "stand_up": "animations/Stand Up.fbx",
        "walking_arc_left": "animations/Walking Arc Left.fbx",
    },
    
    # Audio généré par le TTS (peut être remplacé par env var)
    "audio_file": _audio_file_from_env if _audio_file_from_env else "data/audio.mp3",
    
    # Sortie (peut être remplacé par env var)
    "output_file": _output_file_from_env if _output_file_from_env else "renders/jt_output.mp4",
    
    # Timing
    "camera_zoom_duration": 2.0,  # Secondes de zoom caméra au début
    
    # FPS
    "fps": 30,
}


def clear_scene():
    """Nettoye les objets orphelins mais garde le studio"""
    print("🧹 Nettoyage de la scène...")
    # On ne supprime rien - le studio est déjà là
    # On supprime juste Kara si elle existe déjà (re-run)
    if "Kara" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Kara"], do_unlink=True)
        print("   Kara supprimée (re-import)")


def import_kara(fbx_path):
    """Importe Kara depuis le fichier FBX"""
    print(f"📥 Import de Kara: {fbx_path}")
    
    if not os.path.exists(fbx_path):
        print(f"   ❌ Fichier non trouvé: {fbx_path}")
        return None
    
    # Importer le FBX
    before_objects = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    after_objects = set(bpy.data.objects)
    
    # Trouver le nouvel objet (Kara)
    new_objects = after_objects - before_objects
    if new_objects:
        kara = list(new_objects)[0]
        kara.name = "Kara"
        print(f"   ✅ Kara importée: {kara.name}")
        return kara
    
    print("   ⚠️ Kara non trouvée après import")
    return None


def position_kara(kara):
    """Positionne Kara dans le studio (au bon endroit)"""
    print("📍 Positionnement de Kara...")
    
    if not kara:
        return
    
    # Position - à adapter selon ton studio
    # Kara doit être au centre, près du bureau/écran holographique
    kara.location = (0.0, 0.0, 0.0)  # À ajuster !
    kara.rotation_euler = (0.0, 0.0, 0.0)  # Face caméra
    
    print(f"   Position: {kara.location}")


def load_animation(anim_name, fbx_path):
    """Charge une animation Mixamo et l'ajoute au NLA"""
    print(f"🎭 Chargement animation: {anim_name}")
    
    if not os.path.exists(fbx_path):
        print(f"   ❌ Fichier non trouvé: {fbx_path}")
        return None
    
    # Importer l'animation
    before_actions = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    after_actions = set(bpy.data.actions)
    
    new_actions = after_actions - before_actions
    if new_actions:
        action = list(new_actions)[0]
        action.name = f"Kara_{anim_name}"
        print(f"   ✅ Animation chargée: {action.name} ({action.frame_range[1]} frames)")
        return action
    
    print("   ⚠️ Aucune nouvelle action trouvée")
    return None


def get_audio_duration(audio_path):
    """Calcule la durée de l'audio en secondes"""
    print(f"🎵 Analyse audio: {audio_path}")
    
    if not os.path.exists(audio_path):
        print("   ⚠️ Fichier audio non trouvé, durée par défaut: 60s")
        return 60.0
    
    try:
        import wave
        with wave.open(audio_path, 'r') as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)
            print(f"   ✅ Durée audio: {duration:.2f} secondes")
            return duration
    except Exception as e:
        print(f"   ⚠️ Erreur lecture audio: {e}, durée par défaut: 60s")
        return 60.0


def add_audio_to_scene(audio_path):
    """Ajoute l'audio à la scène Blender"""
    print(f"🔊 Ajout audio à la scène...")
    
    if not os.path.exists(audio_path):
        print("   ⚠️ Fichier audio non trouvé")
        return
    
    # Vérifier si l'audio existe déjà
    for seq in bpy.context.scene.sequence_editor.sequences_all:
        if seq.type == 'SOUND':
            bpy.context.scene.sequence_editor.sequences.remove(seq)
    
    # Ajouter le nouvel audio
    if not bpy.context.scene.sequence_editor:
        bpy.context.scene.sequence_editor_create()
    
    bpy.context.scene.sequence_editor.sequences.new_sound(
        "JT_Audio",
        audio_path,
        channel=1,
        frame_start=1
    )
    print("   ✅ Audio ajouté à la timeline")


def setup_timeline(duration_seconds, fps=30):
    """Configure la timeline Blender"""
    total_frames = int(duration_seconds * fps)
    
    print(f"⏱️ Configuration timeline:")
    print(f"   Durée: {duration_seconds:.2f} secondes")
    print(f"   FPS: {fps}")
    print(f"   Total frames: {total_frames}")
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames
    bpy.context.scene.render.fps = fps
    
    return total_frames


def setup_camera_animation(duration_seconds, fps=30):
    """Gère l'animation de la caméra"""
    print("📹 Configuration caméra...")
    
    zoom_frames = int(CONFIG["camera_zoom_duration"] * fps)
    
    # Trouver la caméra active
    camera = bpy.context.scene.camera
    if not camera:
        # Chercher une caméra dans la scène
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA':
                camera = obj
                bpy.context.scene.camera = camera
                break
    
    if camera:
        print(f"   Caméra trouvée: {camera.name}")
        print(f"   Animation zoom: frames 1 à {zoom_frames}")
        print(f"   Plan fixe: frames {zoom_frames} à {int(duration_seconds * fps)}")
        
        # L'animation de zoom est déjà dans le .blend (frames 1-60 environ)
        # On la garde telle quelle pour les 2 premières secondes
        
        # Optionnel: Ajouter un keyframe pour fixer la position après le zoom
        # Si l'animation de zoom s'arrête à la frame 60, on fixe la caméra après
        pass
    else:
        print("   ⚠️ Aucune caméra trouvée !")


def setup_render_settings(output_path):
    """Configure les paramètres de rendu"""
    print("🎬 Configuration rendu...")
    
    # Format vidéo
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    
    # Résolution (vertical pour TikTok/Shorts)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    # Fichier de sortie
    bpy.context.scene.render.filepath = output_path
    
    print(f"   Résolution: 1080x1920")
    print(f"   Codec: H264")
    print(f"   Sortie: {output_path}")


def create_animation_sequence(kara, actions, total_frames, fps):
    """Crée la séquence d'animations pour Kara"""
    print("🎭 Création séquence d'animations...")
    
    if not kara or not actions:
        print("   ⚠️ Pas de personnage ou d'actions")
        return
    
    zoom_frames = int(CONFIG["camera_zoom_duration"] * fps)
    remaining_frames = total_frames - zoom_frames
    
    # Séquence type pour un JT :
    # 1. Stand To Sit (Kara s'assoit) - pendant le zoom caméra
    # 2. Sitting Talking (Kara présente) - le reste du temps
    
    current_frame = 1
    
    # Animation 1: Stand To Sit (pendant le zoom)
    if "stand_to_sit" in actions and actions["stand_to_sit"]:
        action = actions["stand_to_sit"]
        duration = action.frame_range[1] - action.frame_range[0]
        print(f"   Frame {current_frame}: Stand To Sit ({duration} frames)")
        
        # Assigner l'action
        if kara.animation_data:
            kara.animation_data.action = action
        else:
            kara.animation_data_create()
            kara.animation_data.action = action
        
        current_frame += int(duration)
    
    # Animation 2: Sitting Talking (le reste du JT)
    if "sitting_talking" in actions and actions["sitting_talking"]:
        action = actions["sitting_talking"]
        print(f"   Frame {current_frame} à {total_frames}: Sitting Talking (loop)")
        
        # Créer une boucle de l'animation pour toute la durée
        # On utilise le NLA pour ça
        # Pour faire simple: on étend l'action
        
        # Alternative simple: répéter l'animation manuellement avec des keyframes
        # Ou utiliser le NLA Editor pour mixer les animations
        pass
    
    print("   ✅ Séquence créée")


def render_animation():
    """Lance le rendu de l'animation"""
    print("🎨 Lancement du rendu...")
    print("   ⏳ Cela peut prendre plusieurs minutes...")
    
    # Rendu de l'animation
    bpy.ops.render.render(animation=True)
    
    print("   ✅ Rendu terminé !")


# ============================================================
# MAIN
# ============================================================

def main():
    """Fonction principale - exécutée par Blender"""
    print("=" * 60)
    print("🎬 BLENDER SCRIPT - JT 3D AUTOMATION")
    print("=" * 60)
    
    # 1. Nettoyer
    clear_scene()
    
    # 2. Importer Kara
    kara = import_kara(CONFIG["kara_fbx"])
    if kara:
        position_kara(kara)
    
    # 3. Charger les animations
    actions = {}
    for anim_name, anim_path in CONFIG["animations"].items():
        action = load_animation(anim_name, anim_path)
        if action:
            actions[anim_name] = action
    
    # 4. Calculer la durée de l'audio
    audio_duration = get_audio_duration(CONFIG["audio_file"])
    
    # 5. Configurer la timeline
    total_frames = setup_timeline(audio_duration, CONFIG["fps"])
    
    # 6. Ajouter l'audio
    add_audio_to_scene(CONFIG["audio_file"])
    
    # 7. Configurer la caméra
    setup_camera_animation(audio_duration, CONFIG["fps"])
    
    # 8. Créer la séquence d'animations
    create_animation_sequence(kara, actions, total_frames, CONFIG["fps"])
    
    # 9. Configurer le rendu
    setup_render_settings(CONFIG["output_file"])
    
    # 10. Lancer le rendu
    render_animation()
    
    print("=" * 60)
    print("✅ BLENDER SCRIPT TERMINÉ")
    print("=" * 60)


# Exécuter si appelé directement
if __name__ == "__main__":
    main()
