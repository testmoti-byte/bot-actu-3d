#!/usr/bin/env python3
"""
Blender Script - VERSION FINALE COMPLETE
Les personnages et animations sont DÉJÀ dans le .blend

Fonctionnalités:
1. Chemin pour marcher jusqu'à la chaise
2. Enchaînement des animations (Walk → Sit → Talk)
3. Rotation chaise sens HORAIRE (aiguilles d'une montre)
4. Easing/balancement pour transitions fluides
5. Tête suit la caméra
"""

import bpy
import os
import sys
import math
from math import pi

# ============================================================
# CONFIGURATION
# ============================================================

_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
print(f"📁 Dossier du .blend: {blend_dir}")

AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

FPS = 30

# Noms des animations (à ajuster selon tes noms exacts)
ANIM_WALK = "F Walking Arc Left"      # Marche
ANIM_SIT = "F Stand To Sit"           # S'assoit
ANIM_TALK = "F Sitting Talking"       # Parle assis
ANIM_IDLE = "F attendre"              # Attente

# Durées (en secondes)
WALK_DURATION = 3.0
SIT_DURATION = 2.5
CHAIR_TURN_DURATION = 1.0

# Rotation chaise (NÉGATIF = sens HORAIRE)
CHAIR_ROTATION = -140  # degrés

# Distance de marche (en unités Blender, probablement mm)
WALK_DISTANCE = 800

# Balancement (easing)
BOUNCE_AMOUNT = 0.15   # Intensité du rebond (0.1 = 10%)
BOUNCE_FRAMES = 15     # Durée du rebond en frames

print("=" * 60)
print("🎬 BLENDER SCRIPT - VERSION FINALE")
print("=" * 60)


def find_character():
    """Trouve le personnage principal (armature)"""
    print(f"\n🔍 Recherche du personnage...")
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            if len(obj.pose.bones) > 10:
                print(f"   ✅ Trouvé: {obj.name}")
                print(f"      📍 Location: {tuple(round(l, 2) for l in obj.location)}")
                return obj
    
    print(f"   ❌ Aucun personnage trouvé")
    return None


def find_chair():
    """Trouve la chaise"""
    print(f"\n🪑 Recherche chaise...")
    
    for obj in bpy.context.scene.objects:
        name_lower = obj.name.lower()
        if any(kw in name_lower for kw in ["chaise", "chair", "seat", "fauteuil"]):
            print(f"   ✅ Trouvée: {obj.name}")
            return obj
    
    print(f"   ⚠️ Non trouvée")
    return None


def find_camera():
    """Trouve la caméra active"""
    cam = bpy.context.scene.camera
    if cam:
        print(f"\n📹 Caméra: {cam.name}")
        return cam
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            print(f"\n📹 Caméra trouvée: {obj.name}")
            return obj
    
    return None


def get_action(name):
    """Récupère une action par son nom (recherche flexible)"""
    # Recherche exacte
    if name in bpy.data.actions:
        return bpy.data.actions[name]
    
    # Recherche partielle
    for action in bpy.data.actions:
        if name.lower() in action.name.lower():
            print(f"   ✅ Action trouvée: {action.name}")
            return action
    
    print(f"   ⚠️ Action non trouvée: {name}")
    return None


def setup_head_tracking(character, camera):
    """La tête suit la caméra"""
    print(f"\n👀 Configuration suivi de tête...")
    
    if not character or not camera:
        return
    
    # Trouver la bone de la tête
    head_bone = None
    for bone in character.pose.bones:
        name_lower = bone.name.lower()
        if any(kw in name_lower for kw in ["head", "tête", "tete", "neck"]):
            head_bone = bone
            break
    
    if not head_bone:
        print(f"   ⚠️ Bone tête non trouvée")
        return
    
    # Supprimer ancien constraint
    for c in head_bone.constraints:
        if c.type == 'TRACK_TO':
            head_bone.constraints.remove(c)
    
    # Ajouter Track To
    track = head_bone.constraints.new('TRACK_TO')
    track.target = camera
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    
    print(f"   ✅ Tête suit la caméra (bone: {head_bone.name})")


def apply_easing(fcurves, start_frame, end_frame, bounce=True):
    """
    Applique un easing avec rebond sur les keyframes
    Pour que ça s'arrête pas net
    """
    if not bounce or not fcurves:
        return
    
    for fcurve in fcurves:
        keyframes = [k for k in fcurve.keyframe_points if start_frame <= k.co[0] <= end_frame]
        
        for k in keyframes:
            # Interpolation bézier pour plus fluide
            k.interpolation = 'BEZIER'
            
            # Ajouter du rebond sur les keyframes de fin
            if k.co[0] == end_frame:
                # Handles pour effet de rebond léger
                k.handle_left_type = 'AUTO'
                k.handle_right_type = 'AUTO'


def create_walk_path(character, start_frame, end_frame):
    """
    Crée un chemin de marche avec mouvement naturel
    Le personnage avance vers la chaise
    """
    print(f"\n🚶 Création chemin de marche...")
    
    if not character:
        return
    
    # Position de départ
    start_pos = character.location.copy()
    
    # Position d'arrivée (devant la chaise)
    end_pos = start_pos.copy()
    end_pos[1] += WALK_DISTANCE  # Avancer sur Y
    
    # Créer les keyframes de position
    character.location = start_pos
    character.keyframe_insert(data_path="location", frame=start_frame)
    
    character.location = end_pos
    character.keyframe_insert(data_path="location", frame=end_frame)
    
    # Appliquer l'animation de marche
    walk_action = get_action(ANIM_WALK)
    if walk_action and character.animation_data:
        character.animation_data.action = walk_action
    
    print(f"   ✅ Chemin créé: frames {start_frame} à {end_frame}")


def play_animation(character, action_name, start_frame):
    """Joue une animation à un frame donné"""
    action = get_action(action_name)
    if not action:
        return 0
    
    if character.animation_data:
        character.animation_data.action = action
    
    # Durée de l'action
    duration = int((action.frame_range[1] - action.frame_range[0]) / FPS)
    print(f"   🎬 {action_name}: {duration}s")
    
    return duration


def animate_chair(chair, start_frame, duration_frames):
    """
    Anime la rotation de la chaise
    SENS HORAIRE + rebond
    """
    print(f"\n🪑 Animation chaise (sens horaire)...")
    
    if not chair:
        return
    
    end_frame = start_frame + duration_frames
    bounce_frame = end_frame + BOUNCE_FRAMES
    
    # Position initiale
    initial_z = chair.rotation_euler[2]
    
    # Keyframe avant rotation
    chair.keyframe_insert(data_path="rotation_euler", frame=start_frame - 1)
    
    # Rotation finale (NÉGATIF = horaire)
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(CHAIR_ROTATION)
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    
    # REBOND: La chaise dépasse légèrement puis revient
    over_rotate = math.radians(CHAIR_ROTATION * BOUNCE_AMOUNT)
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(CHAIR_ROTATION) + over_rotate
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame + BOUNCE_FRAMES // 2)
    
    # Retour position finale
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(CHAIR_ROTATION)
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=bounce_frame)
    
    print(f"   ✅ Rotation {CHAIR_ROTATION}° + rebond")


def get_audio_duration():
    if not os.path.exists(AUDIO_FILE):
        return 30.0
    try:
        from mutagen.mp3 import MP3
        return MP3(AUDIO_FILE).info.length
    except:
        return 30.0


def setup_timeline(duration):
    frames = int(duration * FPS)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.fps = FPS
    print(f"\n⏱️ Timeline: 1 à {frames} frames ({duration:.1f}s)")
    return frames


def add_audio():
    if not os.path.exists(AUDIO_FILE):
        return
    try:
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        for seq in list(bpy.context.scene.sequence_editor.sequences_all):
            if seq.type == 'SOUND':
                bpy.context.scene.sequence_editor.sequences.remove(seq)
        bpy.context.scene.sequence_editor.sequences.new_sound("Audio", AUDIO_FILE, 1, 1)
        print(f"\n🔊 Audio ajouté")
    except Exception as e:
        print(f"   ⚠️ Erreur audio: {e}")


def setup_render():
    print(f"\n🎬 Configuration rendu...")
    
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    try:
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.filepath = OUTPUT_FILE
        print(f"   Format: MP4")
    except:
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = OUTPUT_FILE.replace('.mp4', '_frame_')
        print(f"   Format: PNG")


def render():
    print(f"\n🎨 Rendu en cours...")
    try:
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"   ✅ Terminé!")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")


def main():
    print("\n" + "=" * 60)
    print("🎬 BLENDER SCRIPT - DÉBUT")
    print("=" * 60)
    
    try:
        # Afficher les actions disponibles
        print(f"\n📋 Actions disponibles:")
        for action in bpy.data.actions:
            print(f"   - {action.name}")
        
        # Trouver les objets
        character = find_character()
        chair = find_chair()
        camera = find_camera()
        
        if not character:
            print("❌ Pas de personnage!")
            return
        
        # Configuration tête suit caméra
        if camera:
            setup_head_tracking(character, camera)
        
        # Durée totale
        duration = get_audio_duration()
        total_frames = setup_timeline(duration)
        
        # === SÉQUENCE D'ANIMATION ===
        print(f"\n🎭 Création séquence...")
        
        current_frame = 1
        
        # 1. MARCHE vers la chaise
        walk_end = int(WALK_DURATION * FPS)
        create_walk_path(character, current_frame, walk_end)
        play_animation(character, ANIM_WALK, current_frame)
        current_frame = walk_end
        
        # 2. S'ASSOIT
        sit_end = current_frame + int(SIT_DURATION * FPS)
        play_animation(character, ANIM_SIT, current_frame)
        current_frame = sit_end
        
        # 3. TOURNER CHAISE (avec rebond)
        chair_frames = int(CHAIR_TURN_DURATION * FPS)
        animate_chair(chair, current_frame, chair_frames)
        current_frame += chair_frames + BOUNCE_FRAMES
        
        # 4. PARLER (reste du temps)
        play_animation(character, ANIM_TALK, current_frame)
        
        # Audio et rendu
        add_audio()
        setup_render()
        render()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎬 FIN")
    print("=" * 60)


main()
