#!/usr/bin/env python3
"""
Blender Script - VERSION INTELLIGENTE
Calcule automatiquement les positions et crée l'animation

Fonctionnalités:
1. Détecte la position de la chaise
2. Calcule la position de départ du personnage (hors champ)
3. Crée le chemin automatiquement
4. Gère arrivée gauche/droite
5. Rotation chaise adaptative
6. Tête suit la caméra
"""

import bpy
import os
import sys
import math
import random
from math import pi

# ============================================================
# CONFIGURATION
# ============================================================

_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
print(f"📁 Dossier: {blend_dir}")

AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

FPS = 30

# Noms des animations (ajuster selon tes noms)
ANIM_WALK = "F Walking Arc Left"
ANIM_SIT = "F Stand To Sit"
ANIM_TALK = "F Sitting Talking"
ANIM_IDLE = "F attendre"

# Durées
WALK_DURATION = 3.0
SIT_DURATION = 2.5
CHAIR_TURN_DURATION = 1.0

# Distance hors champ (en unités Blender)
OFFSCREEN_DISTANCE = 1500  # mm derrière/de côté

# Mode arrivée: "left", "right", "random"
ARRIVAL_MODE = "random"

# Rotation chaise base
CHAIR_ROTATION_BASE = -140  # degrés (négatif = horaire)

# Balancement
BOUNCE_AMOUNT = 0.15
BOUNCE_FRAMES = 15

print("=" * 60)
print("🎬 BLENDER SCRIPT - VERSION INTELLIGENTE")
print("=" * 60)


def find_all_characters():
    """Trouve tous les personnages (armatures)"""
    print(f"\n🔍 Recherche des personnages...")
    
    characters = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE' and len(obj.pose.bones) > 10:
            characters.append(obj)
            print(f"   ✅ {obj.name}")
            print(f"      📍 Position: {tuple(round(v, 2) for v in obj.location)}")
    
    return characters


def find_chair():
    """Trouve la chaise et sa position"""
    print(f"\n🪑 Recherche chaise...")
    
    for obj in bpy.context.scene.objects:
        name_lower = obj.name.lower()
        if any(kw in name_lower for kw in ["chaise", "chair", "seat", "fauteuil"]):
            print(f"   ✅ Trouvée: {obj.name}")
            print(f"      📍 Position: {tuple(round(v, 2) for v in obj.location)}")
            print(f"      📐 Rotation Z: {math.degrees(obj.rotation_euler[2]):.1f}°")
            return obj
    
    print(f"   ⚠️ Non trouvée")
    return None


def find_camera():
    """Trouve la caméra active"""
    cam = bpy.context.scene.camera
    if cam:
        print(f"\n📹 Caméra active: {cam.name}")
        print(f"      📍 Position: {tuple(round(v, 2) for v in cam.location)}")
        return cam
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            print(f"\n📹 Caméra: {obj.name}")
            return obj
    
    return None


def calculate_scene_positions(chair, camera, arrival="random"):
    """
    Calcule toutes les positions nécessaires pour l'animation
    Retourne: dict avec start_pos, end_pos, chair_rotation
    """
    print(f"\n📐 Calcul des positions...")
    
    if not chair:
        print("   ❌ Pas de chaise pour calculer")
        return None
    
    # Position de la chaise
    chair_pos = chair.location.copy()
    chair_rot = chair.rotation_euler[2]
    
    print(f"   🪑 Chaise position: {chair_pos}")
    print(f"   🪑 Chaise rotation: {math.degrees(chair_rot):.1f}°")
    
    # Déterminer le côté d'arrivée
    if arrival == "random":
        arrival = random.choice(["left", "right"])
    
    print(f"   🚶 Arrivée: {arrival}")
    
    # Calculer la position de départ (hors champ, sur le côté)
    start_pos = chair_pos.copy()
    
    if arrival == "left":
        # Arriver par la gauche
        start_pos[0] -= OFFSCREEN_DISTANCE  # X négatif = gauche
        chair_rotation = CHAIR_ROTATION_BASE  # Rotation standard
    else:
        # Arriver par la droite
        start_pos[0] += OFFSCREEN_DISTANCE  # X positif = droite
        chair_rotation = -CHAIR_ROTATION_BASE  # Rotation inversée
    
    # Position finale = devant la chaise (légèrement devant)
    end_pos = chair_pos.copy()
    end_pos[1] += 200  # Un peu devant la chaise
    
    # Calculer la distance à parcourir
    distance = math.sqrt(
        (end_pos[0] - start_pos[0])**2 + 
        (end_pos[1] - start_pos[1])**2
    )
    
    print(f"   📍 Départ: {tuple(round(v, 1) for v in start_pos)}")
    print(f"   📍 Arrivée: {tuple(round(v, 1) for v in end_pos)}")
    print(f"   📏 Distance: {distance:.0f}")
    print(f"   🔄 Rotation chaise: {chair_rotation}°")
    
    return {
        "start_pos": start_pos,
        "end_pos": end_pos,
        "chair_rotation": chair_rotation,
        "arrival": arrival,
        "distance": distance
    }


def position_character(character, start_pos):
    """Place le personnage à sa position de départ"""
    print(f"\n👤 Positionnement de {character.name}...")
    
    character.location = start_pos
    print(f"   ✅ Positionné à: {tuple(round(v, 1) for v in start_pos)}")


def get_action(name):
    """Récupère une action par son nom (flexible)"""
    if name in bpy.data.actions:
        return bpy.data.actions[name]
    
    for action in bpy.data.actions:
        if name.lower() in action.name.lower():
            return action
    
    return None


def setup_head_tracking(character, camera):
    """La tête suit la caméra"""
    if not character or not camera:
        return
    
    print(f"\n👀 Configuration tête...")
    
    head_bone = None
    for bone in character.pose.bones:
        name_lower = bone.name.lower()
        if any(kw in name_lower for kw in ["head", "tête", "tete"]):
            head_bone = bone
            break
    
    if not head_bone:
        print("   ⚠️ Bone tête non trouvée")
        return
    
    # Supprimer ancien constraint
    for c in head_bone.constraints:
        if c.type == 'TRACK_TO':
            head_bone.constraints.remove(c)
    
    track = head_bone.constraints.new('TRACK_TO')
    track.target = camera
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    
    print(f"   ✅ Tête suit caméra")


def create_walk_animation(character, start_pos, end_pos, start_frame, end_frame):
    """Crée l'animation de marche avec position"""
    print(f"\n🚶 Animation marche...")
    
    # Animation de position
    character.location = start_pos
    character.keyframe_insert(data_path="location", frame=start_frame)
    
    character.location = end_pos
    character.keyframe_insert(data_path="location", frame=end_frame)
    
    # Appliquer l'animation de marche
    walk_action = get_action(ANIM_WALK)
    if walk_action and character.animation_data:
        character.animation_data.action = walk_action
        print(f"   ✅ Action: {walk_action.name}")
    
    print(f"   ✅ Frames {start_frame} à {end_frame}")


def animate_chair_smart(chair, rotation_deg, start_frame, duration_frames):
    """
    Anime la chaise avec rotation adaptative
    """
    print(f"\n🪑 Animation chaise...")
    
    if not chair:
        return
    
    end_frame = start_frame + duration_frames
    bounce_frame = end_frame + BOUNCE_FRAMES
    
    initial_z = chair.rotation_euler[2]
    
    # Keyframe initial
    chair.keyframe_insert(data_path="rotation_euler", frame=start_frame - 1)
    
    # Rotation finale
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(rotation_deg)
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    
    # Rebond
    over_rotate = math.radians(rotation_deg * BOUNCE_AMOUNT)
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(rotation_deg) + over_rotate
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame + BOUNCE_FRAMES // 2)
    
    # Retour
    chair.rotation_euler = (
        chair.rotation_euler[0],
        chair.rotation_euler[1],
        initial_z + math.radians(rotation_deg)
    )
    chair.keyframe_insert(data_path="rotation_euler", frame=bounce_frame)
    
    print(f"   ✅ Rotation: {rotation_deg}° + rebond")


def play_action(character, action_name, frame):
    """Joue une action"""
    action = get_action(action_name)
    if action and character.animation_data:
        character.animation_data.action = action
        print(f"   🎬 {action_name}")
        return int((action.frame_range[1] - action.frame_range[0]) / FPS)
    return 0


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
    print(f"\n⏱️ Timeline: {frames} frames ({duration:.1f}s)")
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
        print(f"   ⚠️ Erreur: {e}")


def setup_render():
    print(f"\n🎬 Rendu...")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    
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


def hide_other_characters(characters, selected):
    """Cache les autres personnages"""
    for char in characters:
        if char != selected:
            char.hide_render = True
            char.hide_viewport = True


def main():
    print("\n" + "=" * 60)
    print("🎬 SCRIPT INTELLIGENT - DÉBUT")
    print("=" * 60)
    
    try:
        # Lister les actions
        print(f"\n📋 Actions disponibles:")
        for action in bpy.data.actions:
            print(f"   - {action.name}")
        
        # Trouver les éléments
        characters = find_all_characters()
        chair = find_chair()
        camera = find_camera()
        
        if not characters:
            print("❌ Aucun personnage!")
            return
        
        if not chair:
            print("❌ Pas de chaise!")
            return
        
        # Sélectionner le premier personnage
        character = characters[0]
        print(f"\n👤 Personnage sélectionné: {character.name}")
        
        # Cacher les autres
        hide_other_characters(characters, character)
        
        # Calculer les positions automatiquement
        positions = calculate_scene_positions(chair, camera, ARRIVAL_MODE)
        
        if not positions:
            print("❌ Impossible de calculer les positions!")
            return
        
        # Positionner le personnage au départ
        position_character(character, positions["start_pos"])
        
        # Configurer la tête
        if camera:
            setup_head_tracking(character, camera)
        
        # Durée
        duration = get_audio_duration()
        total_frames = setup_timeline(duration)
        
        # === SÉQUENCE ===
        print(f"\n🎭 Création séquence...")
        
        current_frame = 1
        
        # 1. MARCHE
        walk_end = current_frame + int(WALK_DURATION * FPS)
        create_walk_animation(
            character, 
            positions["start_pos"],
            positions["end_pos"],
            current_frame,
            walk_end
        )
        current_frame = walk_end
        
        # 2. S'ASSOIT
        sit_end = current_frame + int(SIT_DURATION * FPS)
        play_action(character, ANIM_SIT, current_frame)
        current_frame = sit_end
        
        # 3. ROTATION CHAISE
        chair_frames = int(CHAIR_TURN_DURATION * FPS)
        animate_chair_smart(
            chair, 
            positions["chair_rotation"],
            current_frame,
            chair_frames
        )
        current_frame += chair_frames + BOUNCE_FRAMES
        
        # 4. PARLER
        play_action(character, ANIM_TALK, current_frame)
        
        # Audio et rendu
        add_audio()
        setup_render()
        render()
        
        print(f"\n✅ Animation terminée!")
        print(f"   Arrivée: {positions['arrival']}")
        print(f"   Distance parcourue: {positions['distance']:.0f}")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎬 FIN")
    print("=" * 60)


main()
