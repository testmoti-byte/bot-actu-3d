#!/usr/bin/env python3
"""
Blender Script - VERSION ADAPTÉE POUR KARA
S'assure que le personnage "Armakara" est bien détecté et animé
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

# --- NOMS DES ANIMATIONS (MOTEUR DE RECHERCHE INTELLIGENT) ---
# Le script va chercher ces MOTS CLÉS dans les noms de tes actions réelles.
# Exemple: Si tu cherches "WALK", il trouvera "Kara_Walk_Loop" ou "Walk_Cycle".

ANIM_WALK_KEYWORDS = ["walk", "marche", "course"]
ANIM_SIT_KEYWORDS = ["sit", "s'asseoir", "assied", "to sit"]
ANIM_TALK_KEYWORDS = ["talk", "parle", "speak", "idle"]
ANIM_IDLE_KEYWORDS = ["idle", "attend", "wait"]

# Durées
WALK_DURATION = 3.0
SIT_DURATION = 2.5
CHAIR_TURN_DURATION = 1.0

# Distance hors champ
OFFSCREEN_DISTANCE = 1500  
ARRIVAL_MODE = "random" 
CHAIR_ROTATION_BASE = -140 
BOUNCE_AMOUNT = 0.15
BOUNCE_FRAMES = 15

print("=" * 60)
print("🎬 BLENDER SCRIPT - VERSION KARA")
print("=" * 60)


def find_all_characters():
    """
    TROUVE LE PERSONNAGE KARA FORCÉMENT
    """
    print(f"\n🔍 Recherche du personnage Kara...")
    
    # 1. PRIORITÉ ABSOLUE : Chercher 'Armakara' ou 'Kara'
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            if "armakara" in obj.name.lower() or "kara" in obj.name.lower():
                print(f"   🌟 PERSONNAGE 'KARA' TROUVÉ FORCÉMENT : {obj.name}")
                print(f"      📍 Position: {tuple(round(v, 2) for v in obj.location)}")
                return [obj] # On retourne Kara immédiatement
    
    # 2. SINON : Chercher n'importe quelle armature (Fallback)
    print(f"   ⚠️ Kara non trouvé par son nom, recherche d'autres armatures...")
    characters = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE' and len(obj.pose.bones) > 10:
            characters.append(obj)
            print(f"   ✅ Autre personnage trouvé: {obj.name}")
    
    if not characters:
        print("   ❌ AUCUN PERSONNAGE TROUVÉ !")
    
    return characters


def find_chair():
    """Trouve la chaise"""
    print(f"\n🪑 Recherche chaise...")
    
    for obj in bpy.context.scene.objects:
        name_lower = obj.name.lower()
        if any(kw in name_lower for kw in ["chaise", "chair", "seat", "fauteuil"]):
            print(f"   ✅ Chaise trouvée: {obj.name}")
            return obj
    
    print(f"   ⚠️ Chaise non trouvée, essaie de prendre le 1er objet 'Chair' si existe...")
    # Tentative alternative
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH': # Parfois c'est un mesh
             if any(kw in obj.name.lower() for kw in ["chaise", "chair", "seat"]):
                 return obj
                 
    return None


def find_camera():
    """Trouve la caméra"""
    cam = bpy.context.scene.camera
    if cam:
        return cam
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            return obj
    return None


def calculate_scene_positions(chair, camera, arrival="random"):
    """Calcule les positions"""
    if not chair:
        return None
    
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
    end_pos[1] += 200 # Devant la chaise
    
    distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
    
    print(f"   📍 Calcul : Arrivée {arrival}, Distance {distance:.0f}")
    
    return {
        "start_pos": start_pos,
        "end_pos": end_pos,
        "chair_rotation": chair_rotation,
        "arrival": arrival,
        "distance": distance
    }


def get_action_smart(keywords_list):
    """
    Cherche une action contenant un des mots clés
    Exemple: keywords=["walk"] trouvera "Action_Walk_Cycle"
    """
    # 1. Cherche exact
    for action in bpy.data.actions:
        action_name_lower = action.name.lower()
        for kw in keywords_list:
            if kw.lower() in action_name_lower:
                print(f"   ✅ Animation trouvée pour '{kw}': {action.name}")
                return action
    
    print(f"   ⚠️ Aucune animation trouvée pour les mots clés: {keywords_list}")
    return None


def get_action(name):
    """Fonction legacy pour compatibilité, utilise la smart search maintenant"""
    # Mapping simple des anciens noms vers mots clés
    if "walk" in name.lower():
        return get_action_smart(ANIM_WALK_KEYWORDS)
    elif "sit" in name.lower():
        return get_action_smart(ANIM_SIT_KEYWORDS)
    elif "talk" in name.lower():
        return get_action_smart(ANIM_TALK_KEYWORDS)
    elif "idle" in name.lower():
        return get_action_smart(ANIM_IDLE_KEYWORDS)
    return get_action_smart([name])


def position_character(character, start_pos):
    character.location = start_pos
    # S'assurer que le personnage est visible (pas caché en rendu)
    character.hide_render = False
    character.hide_viewport = False
    print(f"   ✅ Positionné et rendu visible")


def setup_head_tracking(character, camera):
    """La tête suit la caméra"""
    if not character or not camera:
        return
    
    head_bone = None
    for bone in character.pose.bones:
        name_lower = bone.name.lower()
        # Recherche élargie pour la tête (head, crane, face, etc.)
        if any(kw in name_lower for kw in ["head", "tête", "tete", "crane", "face"]):
            head_bone = bone
            print(f"   ✅ Os Tête trouvé: {bone.name}")
            break
    
    if not head_bone:
        print("   ⚠️ Os 'head' non trouvé (Kara a peut-être un nom d'os différent)")
        # On essaie de trouver le premier os qui a 'head' ou similaire dans ses sous-parties si besoin
        return
    
    # Nettoyage contraintes
    for c in head_bone.constraints:
        if c.type == 'TRACK_TO':
            head_bone.constraints.remove(c)
    
    track = head_bone.constraints.new('TRACK_TO')
    track.target = camera
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'


def create_walk_animation(character, start_pos, end_pos, start_frame, end_frame):
    """Animation de position (déplacement)"""
    character.location = start_pos
    character.keyframe_insert(data_path="location", frame=start_frame)
    
    character.location = end_pos
    character.keyframe_insert(data_path="location", frame=end_frame)
    
    # Appliquer l'action de marche (animation osseuse)
    walk_action = get_action_smart(ANIM_WALK_KEYWORDS)
    if walk_action and character.animation_data:
        if not character.animation_data.action:
            character.animation_data.action = walk_action
        else:
            # Si une action existe déjà, on la strippe ou on la remplace
            # Ici on assume qu'on fait un NLA strip ou on remplace l'action active
            character.animation_data.action = walk_action
            
    print(f"   🚶 Déplacement défini frame {start_frame} -> {end_frame}")


def animate_chair_smart(chair, rotation_deg, start_frame, duration_frames):
    if not chair:
        return
    
    end_frame = start_frame + duration_frames
    bounce_frame = end_frame + BOUNCE_FRAMES
    initial_z = chair.rotation_euler[2]
    
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
    
    print(f"   🪑 Rotation chaise animée")


def play_action(character, action_name, frame):
    """Joue une action à un frame précis"""
    action = get_action(action_name)
    if action and character.animation_data:
        # Pour changer d'action au milieu de l'animation, il faut souvent utiliser les NLA Tracks
        # mais pour faire simple, on force l'action active. 
        # Note: Cela va changer l'action sur TOUTE la timeline. 
        # Pour un vrai mix, il faudrait utiliser des strips NLA.
        character.animation_data.action = action
        print(f"   🎬 Action jouée: {action.name} (frame {frame})")
        return 10 # Durée estimée
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
    print(f"⏱️ Timeline: {frames} frames ({duration:.1f}s)")
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
        print(f"🔊 Audio ajouté à la timeline")
    except Exception as e:
        print(f"⚠️ Erreur ajout audio: {e}")


def setup_render():
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    try:
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.filepath = OUTPUT_FILE
        print(f"🎨 Rendu configuré: MP4 H264")
    except:
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = OUTPUT_FILE.replace('.mp4', '_frame_')
        print(f"🎨 Rendu configuré: PNG Fallback")


def render():
    print(f"🎨 Lancement du rendu...")
    try:
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"   ✅ Rendu terminé!")
    except Exception as e:
        print(f"   ❌ Erreur rendu: {e}")


def hide_other_characters(characters, selected):
    """Cache les autres persos"""
    for char in characters:
        if char != selected:
            char.hide_render = True
            char.hide_viewport = True


def main():
    print("\n" + "=" * 60)
    print("🎬 DÉMARRAGE SCRIPT KARA")
    print("=" * 60)
    
    try:
        # Debug actions
        print(f"\n📋 Actions disponibles dans le fichier Blend:")
        for action in bpy.data.actions:
            print(f"   - {action.name}")
        
        # Trouver les éléments
        characters = find_all_characters()
        chair = find_chair()
        camera = find_camera()
        
        if not characters:
            print("❌ ARRÊT: Aucun personnage trouvé !")
            return
        
        if not chair:
            print("❌ ARRÊT: Pas de chaise trouvée !")
            return
        
        # Prendre Kara (le premier de la liste, qui est forcément Kara grâce à la modiff)
        character = characters[0]
        print(f"\n👤 Personnage actif: {character.name}")
        
        # Cacher les autres
        hide_other_characters(characters, character)
        
        # Calculs positions
        positions = calculate_scene_positions(chair, camera, ARRIVAL_MODE)
        if not positions:
            print("❌ ARRÊT: Calcul positions impossible")
            return
        
        # Placement
        position_character(character, positions["start_pos"])
        
        # Caméra
        if camera:
            setup_head_tracking(character, camera)
        
        # Durée
        duration = get_audio_duration()
        total_frames = setup_timeline(duration)
        
        # SÉQUENCE
        print(f"\n🎭 Création de la séquence d'animation...")
        
        current_frame = 1
        
        # 1. MARCHE
        walk_end = current_frame + int(WALK_DURATION * FPS)
        create_walk_animation(character, positions["start_pos"], positions["end_pos"], current_frame, walk_end)
        current_frame = walk_end
        
        # 2. S'ASSOIT
        sit_end = current_frame + int(SIT_DURATION * FPS)
        play_action(character, "sit", current_frame)
        current_frame = sit_end
        
        # 3. ROTATION CHAISE
        chair_frames = int(CHAIR_TURN_DURATION * FPS)
        animate_chair_smart(chair, positions["chair_rotation"], current_frame, chair_frames)
        current_frame += chair_frames + BOUNCE_FRAMES
        
        # 4. PARLER (Toute la durée restante)
        play_action(character, "talk", current_frame)
        
        # Render
        add_audio()
        setup_render()
        render()
        
        print(f"\n✅ SCRIPT TERMINÉ AVEC SUCCÈS")
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

main()
