#!/usr/bin/env python3
"""
Blender Script - VERSION NOMMAGE CORRECT (arma_kara)
Recherche spécifique de l'armature 'arma_kara' pour animer Kara
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
print(f"📁 Dossier Blender: {blend_dir}")

AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

FPS = 30

# --- NOMS DES ANIMATIONS (TES TERMES EXACTS) ---
ANIM_WALK_KEYWORDS = ["Excited", "Walk", "Marche"]
ANIM_SIT_KEYWORDS = ["Stand To Sit", "Sit", "Assied"]
ANIM_TALK_KEYWORDS = ["Sitting Talking", "Talk", "Parle"]
ANIM_IDLE_KEYWORDS = ["attendre", "Idle"]

# Durées
WALK_DURATION = 3.0
SIT_DURATION = 2.5
CHAIR_TURN_DURATION = 1.0

# Distance hors champ
OFFSCREEN_DISTANCE = 1500  
ARRIVAL_MODE = "random" 

# --- ROTATION CHAISE ---
# -140 degrés = Sens horaire
CHAIR_ROTATION_BASE = -140 

# --- SMOOTHNESS (REBOND) ---
# 0.05 = 5% (Smooth)
BOUNCE_AMOUNT = 0.05 
BOUNCE_FRAMES = 15

print("=" * 60)
print("🎬 BLENDER SCRIPT - CIBLE: ARMA_KARA")
print("=" * 60)


def find_all_characters():
    """
    TROUVE L'ARMATURE 'arma_kara'
    C'est l'objet clé qui contient les animations.
    """
    print(f"\n🔍 Recherche de l'armature arma_kara...")
    
    for obj in bpy.context.scene.objects:
        # On cherche une ARMATURE qui contient "arma_kara" dans son nom
        if obj.type == 'ARMATURE':
            if "arma_kara" in obj.name.lower():
                print(f"   🌟 ARMATURE TROUVÉE : {obj.name}")
                print(f"      📍 Position: {tuple(round(v, 2) for v in obj.location)}")
                return [obj]
    
    # Si on ne trouve pas arma_kara, on cherche une autre armature (Fallback)
    print(f"   ⚠️ 'arma_kara' non trouvé, recherche d'une autre armature...")
    characters = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE' and len(obj.pose.bones) > 10:
            characters.append(obj)
            print(f"   ✅ Autre armature trouvée: {obj.name}")
    
    return characters


def find_chair():
    print(f"\n🪑 Recherche chaise...")
    for obj in bpy.context.scene.objects:
        name_lower = obj.name.lower()
        if any(kw in name_lower for kw in ["chaise", "chair", "seat", "fauteuil"]):
            print(f"   ✅ Chaise trouvée: {obj.name}")
            return obj
    return None


def find_camera():
    cam = bpy.context.scene.camera
    if cam: return cam
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            return obj
    return None


def calculate_scene_positions(chair, camera, arrival="random"):
    if not chair: return None
    chair_pos = chair.location.copy()
    if arrival == "random":
        arrival = random.choice(["left", "right"])
    
    start_pos = chair_pos.copy()
    if arrival == "left":
        start_pos[0] -= OFFSCREEN_DISTANCE
        chair_rotation = CHAIR_ROTATION_BASE
    else:
        start_pos[0] += OFFSCREEN_DISTANCE
        chair_rotation = -CHAIR_ROTATION_BASE 
    
    end_pos = chair_pos.copy()
    end_pos[1] += 200 
    
    print(f"   📍 Calcul : Arrivée {arrival}, Rotation {chair_rotation}°")
    
    return {
        "start_pos": start_pos,
        "end_pos": end_pos,
        "chair_rotation": chair_rotation,
        "arrival": arrival,
        "distance": math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
    }


def get_action_smart(keywords_list):
    """Cherche une action par mot clé exact"""
    for action in bpy.data.actions:
        action_name_lower = action.name.lower()
        for kw in keywords_list:
            if kw.lower() in action_name_lower:
                print(f"   ✅ Action trouvée pour '{kw}': {action.name}")
                return action
    print(f"   ⚠️ Aucune action trouvée pour: {keywords_list}")
    return None


def position_character(character, start_pos):
    character.location = start_pos
    character.hide_render = False
    character.hide_viewport = False
    print(f"   ✅ Positionné")


def setup_head_tracking(character, camera):
    if not character or not camera: return
    for bone in character.pose.bones:
        if any(kw in bone.name.lower() for kw in ["head", "tête", "tete", "crane"]):
            for c in bone.constraints:
                if c.type == 'TRACK_TO': bone.constraints.remove(c)
            track = bone.constraints.new('TRACK_TO')
            track.target = camera
            track.track_axis = 'TRACK_NEGATIVE_Z'
            track.up_axis = 'UP_Y'
            print(f"   ✅ Tête suit caméra")
            break


def create_walk_animation(character, start_pos, end_pos, start_frame, end_frame):
    character.location = start_pos
    character.keyframe_insert(data_path="location", frame=start_frame)
    character.location = end_pos
    character.keyframe_insert(data_path="location", frame=end_frame)
    
    walk_action = get_action_smart(ANIM_WALK_KEYWORDS)
    if walk_action and character.animation_data:
        character.animation_data.action = walk_action
    print(f"   🚶 Walk (Excited) appliqué")


def animate_chair_smart(chair, rotation_deg, start_frame, duration_frames):
    if not chair: return
    end_frame = start_frame + duration_frames
    bounce_frame = end_frame + BOUNCE_FRAMES
    initial_z = chair.rotation_euler[2]
    
    chair.keyframe_insert(data_path="rotation_euler", frame=start_frame - 1)
    
    target_z = initial_z + math.radians(rotation_deg)
    chair.rotation_euler = (chair.rotation_euler[0], chair.rotation_euler[1], target_z)
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    
    over_rotate = math.radians(rotation_deg * BOUNCE_AMOUNT)
    chair.rotation_euler = (chair.rotation_euler[0], chair.rotation_euler[1], target_z + over_rotate)
    chair.keyframe_insert(data_path="rotation_euler", frame=end_frame + BOUNCE_FRAMES // 2)
    
    chair.rotation_euler = (chair.rotation_euler[0], chair.rotation_euler[1], target_z)
    chair.keyframe_insert(data_path="rotation_euler", frame=bounce_frame)
    
    print(f"   🪑 Chaise tournée smooth")


def play_action(character, action_name, frame):
    action = get_action_smart([action_name])
    if action and character.animation_data:
        character.animation_data.action = action
        print(f"   🎬 Action: {action.name}")
    return 0


def get_audio_duration():
    if not os.path.exists(AUDIO_FILE): return 30.0
    try:
        from mutagen.mp3 import MP3
        return MP3(AUDIO_FILE).info.length
    except: return 30.0


def setup_timeline(duration):
    frames = int(duration * FPS)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
    bpy.context.scene.render.fps = FPS
    print(f"⏱️ Timeline: {frames} frames")


def add_audio():
    if not os.path.exists(AUDIO_FILE): return
    try:
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        for seq in list(bpy.context.scene.sequence_editor.sequences_all):
            if seq.type == 'SOUND':
                bpy.context.scene.sequence_editor.sequences.remove(seq)
        bpy.context.scene.sequence_editor.sequences.new_sound("Audio", AUDIO_FILE, 1, 1)
        print(f"🔊 Audio ajouté")
    except Exception as e: print(f"⚠️ Erreur audio: {e}")


def setup_render():
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    try:
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.filepath = OUTPUT_FILE
    except:
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = OUTPUT_FILE.replace('.mp4', '_frame_')


def render():
    print(f"🎨 Rendu...")
    try:
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"✅ Rendu fini")
    except Exception as e:
        print(f"❌ Erreur rendu: {e}")


def hide_other_characters(characters, selected):
    for char in characters:
        if char != selected:
            char.hide_render = True
            char.hide_viewport = True


def main():
    print("\n" + "=" * 60)
    print("🎬 DÉMARRAGE SCRIPT (CIBLE: ARMA_KARA)")
    print("=" * 60)
    
    try:
        characters = find_all_characters()
        chair = find_chair()
        camera = find_camera()
        
        if not characters: 
            print("❌ Aucune armature trouvée !")
            return
        if not chair: 
            print("❌ Pas de chaise !")
            return
        
        character = characters[0]
        hide_other_characters(characters, character)
        
        positions = calculate_scene_positions(chair, camera)
        position_character(character, positions["start_pos"])
        if camera: setup_head_tracking(character, camera)
        
        duration = get_audio_duration()
        setup_timeline(duration)
        
        current_frame = 1
        
        # 1. EXCITED
        walk_end = current_frame + int(WALK_DURATION * FPS)
        create_walk_animation(character, positions["start_pos"], positions["end_pos"], current_frame, walk_end)
        current_frame = walk_end
        
        # 2. STAND TO SIT
        sit_end = current_frame + int(SIT_DURATION * FPS)
        play_action(character, "Stand To Sit", current_frame)
        current_frame = sit_end
        
        # 3. ROTATION CHAISE
        chair_frames = int(CHAIR_TURN_DURATION * FPS)
        animate_chair_smart(chair, positions["chair_rotation"], current_frame, chair_frames)
        current_frame += chair_frames + BOUNCE_FRAMES
        
        # 4. SITTING TALKING
        play_action(character, "Sitting Talking", current_frame)
        
        add_audio()
        setup_render()
        render()
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

main()
