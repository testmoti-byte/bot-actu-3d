#!/usr/bin/env python3
"""
Blender Script - S'exécute DANS Blender
Ce script est appelé par blender_oracle.py

Fonctionnalités :
- Importe Kara dans le studio
- Charge et applique les animations Mixamo
- Gère la séquence d'animation automatique
- Tourne la chaise de bureau
- Synchronise avec l'audio
- Gère les caméras
- Lance le rendu vidéo
"""

import bpy
import os
import sys
import math

# ============================================================
# CONFIGURATION
# ============================================================

# Lire les variables d'environnement passées par blender_oracle.py
_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

# Déterminer le dossier de base (là où est le .blend)
blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
print(f"📁 Dossier du .blend: {blend_dir}")

# Chemins absolus
KARA_PATH = os.path.join(blend_dir, "animations", "KARA_Standing Idle_base_rig.fbx")
ANIMATIONS_DIR = os.path.join(blend_dir, "animations")
AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

# Configuration animation
FPS = 30
KARA_SCALE = 6.5
CHAIR_ROTATION = 140  # degrés

# Positions (à ajuster selon ton studio)
KARA_START_POS = (-500.0, -800.0, 0.0)    # Hors champ, derrière
KARA_END_POS = (0.0, 0.0, 0.0)             # Devant la chaise

# Timing (en secondes)
WALK_DURATION = 2.0      # Temps de marche
SIT_DURATION = 2.0       # Temps pour s'asseoir
CHAIR_TURN_TIME = 0.5    # Temps pour tourner la chaise

print("=" * 60)
print("🎬 BLENDER SCRIPT - CONFIGURATION")
print(f"   Kara: {KARA_PATH}")
print(f"   Animations: {ANIMATIONS_DIR}")
print(f"   Audio: {AUDIO_FILE}")
print(f"   Sortie: {OUTPUT_FILE}")
print("=" * 60)


def check_files():
    """Vérifie que tous les fichiers nécessaires existent"""
    print("\n📂 Vérification des fichiers...")
    
    if os.path.exists(KARA_PATH):
        print(f"   ✅ Kara trouvé")
    else:
        print(f"   ❌ Kara NON trouvé: {KARA_PATH}")
    
    if os.path.exists(ANIMATIONS_DIR):
        print(f"   ✅ Dossier animations trouvé")
        for f in os.listdir(ANIMATIONS_DIR):
            if f.endswith('.fbx'):
                print(f"      - {f}")
    
    if os.path.exists(AUDIO_FILE):
        print(f"   ✅ Audio trouvé")
    else:
        print(f"   ⚠️ Audio NON trouvé (durée par défaut: 30s)")


def clear_scene():
    """Nettoie Kara si elle existe déjà"""
    print("\n🧹 Nettoyage...")
    
    for obj in bpy.data.objects:
        if "Kara" in obj.name or "kara" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"   Supprimé: {obj.name}")
    
    # Supprimer les anciennes actions
    for action in bpy.data.actions:
        if "Kara" in action.name:
            bpy.data.actions.remove(action)


def import_kara():
    """Importe Kara depuis le fichier FBX"""
    print(f"\n📥 Import de Kara...")
    
    if not os.path.exists(KARA_PATH):
        print(f"   ❌ Fichier non trouvé: {KARA_PATH}")
        return None, None
    
    try:
        before_objects = set(bpy.data.objects)
        before_actions = set(bpy.data.actions)
        
        # Importer le FBX
        bpy.ops.import_scene.fbx(filepath=KARA_PATH)
        
        after_objects = set(bpy.data.objects)
        after_actions = set(bpy.data.actions)
        
        new_objects = after_objects - before_objects
        new_actions = after_actions - before_actions
        
        kara_armature = None
        kara_mesh = None
        
        for obj in new_objects:
            if obj.type == 'ARMATURE':
                obj.name = "Kara_Armature"
                kara_armature = obj
                print(f"   ✅ Armature trouvé: {obj.name}")
            elif obj.type == 'MESH':
                obj.name = "Kara_Mesh"
                kara_mesh = obj
                print(f"   ✅ Mesh trouvé: {obj.name}")
        
        # Appliquer l'échelle à l'armature (le mesh suit)
        if kara_armature:
            kara_armature.scale = (KARA_SCALE, KARA_SCALE, KARA_SCALE)
            print(f"   📏 Échelle: x{KARA_SCALE}")
            
            # Position de départ (hors champ)
            kara_armature.location = KARA_START_POS
            print(f"   📍 Position départ: {KARA_START_POS}")
        
        # Vérifier si une animation est déjà présente
        if new_actions:
            for action in new_actions:
                print(f"   🎭 Animation incluse: {action.name}")
        
        return kara_armature, kara_mesh
        
    except Exception as e:
        print(f"   ❌ Erreur import: {e}")
        return None, None


def find_chair():
    """Trouve la chaise dans la scène"""
    print(f"\n🪑 Recherche chaise...")
    
    for obj in bpy.context.scene.objects:
        if "chaise" in obj.name.lower() or "chair" in obj.name.lower():
            print(f"   ✅ Chaise trouvée: {obj.name}")
            return obj
    
    print(f"   ⚠️ Aucune chaise trouvée")
    return None


def find_camera():
    """Trouve la caméra de la scène"""
    print(f"\n📹 Recherche caméra...")
    
    camera = bpy.context.scene.camera
    if camera:
        print(f"   ✅ Caméra active: {camera.name}")
        return camera
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            print(f"   ✅ Caméra trouvée: {obj.name}")
            return obj
    
    print(f"   ⚠️ Aucune caméra trouvée")
    return None


def get_audio_duration():
    """Calcule la durée de l'audio"""
    print(f"\n🎵 Analyse audio...")
    
    if not os.path.exists(AUDIO_FILE):
        print(f"   ⚠️ Audio non trouvé, durée par défaut: 30s")
        return 30.0
    
    try:
        from mutagen.mp3 import MP3
        audio = MP3(AUDIO_FILE)
        duration = audio.info.length
        print(f"   ✅ Durée audio: {duration:.2f} secondes")
        return duration
    except:
        print(f"   ⚠️ Impossible de lire, durée par défaut: 30s")
        return 30.0


def setup_timeline(duration_seconds):
    """Configure la timeline"""
    total_frames = int(duration_seconds * FPS)
    
    print(f"\n⏱️ Configuration timeline:")
    print(f"   Durée: {duration_seconds:.2f} secondes")
    print(f"   FPS: {FPS}")
    print(f"   Frames: 1 à {total_frames}")
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames
    bpy.context.scene.render.fps = FPS
    
    return total_frames


def add_audio():
    """Ajoute l'audio à la scène"""
    print(f"\n🔊 Ajout audio...")
    
    if not os.path.exists(AUDIO_FILE):
        print(f"   ⚠️ Audio non trouvé")
        return
    
    try:
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        
        for seq in bpy.context.scene.sequence_editor.sequences_all:
            if seq.type == 'SOUND':
                bpy.context.scene.sequence_editor.sequences.remove(seq)
        
        bpy.context.scene.sequence_editor.sequences.new_sound(
            "JT_Audio", AUDIO_FILE, channel=1, frame_start=1
        )
        print(f"   ✅ Audio ajouté")
    except Exception as e:
        print(f"   ❌ Erreur audio: {e}")


def create_animation_sequence(kara_armature, chair, total_frames):
    """Crée la séquence d'animations pour le JT"""
    print(f"\n🎭 Création séquence d'animations...")
    
    if not kara_armature:
        print("   ⚠️ Pas d'armature Kara")
        return
    
    # Calculer les frames clés
    start_frame = 1
    
    # Phase 1: Marche vers le bureau (frames 1 à WALK_DURATION*FPS)
    walk_end_frame = int(WALK_DURATION * FPS)
    
    # Phase 2: S'assoit (frames walk_end_frame à walk_end_frame + SIT_DURATION*FPS)
    sit_end_frame = walk_end_frame + int(SIT_DURATION * FPS)
    
    # Phase 3: Tourne la chaise
    chair_turn_frame = sit_end_frame
    
    # Phase 4: Présente le JT (reste du temps)
    
    print(f"   📊 Timeline:")
    print(f"      Frames 1-{walk_end_frame}: Marche vers bureau")
    print(f"      Frames {walk_end_frame}-{sit_end_frame}: S'assoit")
    print(f"      Frame {chair_turn_frame}: Tourne chaise {CHAIR_ROTATION}°")
    print(f"      Frames {sit_end_frame}-{total_frames}: Présente JT")
    
    # ===== ANIMATION DE POSITION (Kara se déplace) =====
    
    # Keyframe de départ
    kara_armature.location = KARA_START_POS
    kara_armature.keyframe_insert(data_path="location", frame=1)
    
    # Keyframe d'arrivée
    kara_armature.location = KARA_END_POS
    kara_armature.keyframe_insert(data_path="location", frame=walk_end_frame)
    
    print(f"   ✅ Animation position créée")
    
    # ===== ANIMATION DE LA CHAISE =====
    
    if chair:
        # Position initiale
        initial_rotation = chair.rotation_euler[2]  # Z rotation
        
        # Keyframe initial
        chair.keyframe_insert(data_path="rotation_euler", frame=sit_end_frame - 1)
        
        # Keyframe rotation
        chair.rotation_euler = (
            chair.rotation_euler[0],
            chair.rotation_euler[1],
            initial_rotation + math.radians(CHAIR_ROTATION)
        )
        chair.keyframe_insert(data_path="rotation_euler", frame=sit_end_frame + int(CHAIR_TURN_TIME * FPS))
        
        print(f"   ✅ Animation chaise créée ({CHAIR_ROTATION}°)")


def setup_render():
    """Configure les paramètres de rendu"""
    print(f"\n🎬 Configuration rendu...")
    
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Résolution (vertical pour TikTok/Shorts)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    # Essayer FFMPEG
    video_format_ok = False
    try:
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        video_format_ok = True
        print(f"   Format: MP4 via FFMPEG")
    except TypeError:
        print(f"   ⚠️ FFMPEG non disponible, sortie en PNG")
    
    if video_format_ok:
        try:
            bpy.context.scene.render.ffmpeg.format = 'MPEG4'
            bpy.context.scene.render.ffmpeg.codec = 'H264'
        except:
            pass
        bpy.context.scene.render.filepath = OUTPUT_FILE
    else:
        png_output = OUTPUT_FILE.replace('.mp4', '_frame_')
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = png_output
        print(f"   ⚠️ ffmpeg nécessaire pour créer la vidéo")
    
    print(f"   Résolution: 1080x1920")


def render():
    """Lance le rendu"""
    print(f"\n🎨 Lancement du rendu...")
    print(f"   ⏳ Patience...")
    
    try:
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"   ✅ Rendu terminé !")
    except Exception as e:
        print(f"   ❌ Erreur rendu: {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("🎬 BLENDER SCRIPT - DÉBUT")
    print("=" * 60)
    
    try:
        # 1. Vérifier les fichiers
        check_files()
        
        # 2. Nettoyer
        clear_scene()
        
        # 3. Importer Kara
        kara_armature, kara_mesh = import_kara()
        
        # 4. Trouver la chaise
        chair = find_chair()
        
        # 5. Calculer la durée
        duration = get_audio_duration()
        
        # 6. Configurer la timeline
        total_frames = setup_timeline(duration)
        
        # 7. Créer la séquence d'animations
        create_animation_sequence(kara_armature, chair, total_frames)
        
        # 8. Ajouter l'audio
        add_audio()
        
        # 9. Trouver la caméra
        find_camera()
        
        # 10. Configurer le rendu
        setup_render()
        
        # 11. Lancer le rendu
        render()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎬 BLENDER SCRIPT - FIN")
    print("=" * 60)


# Exécuter
main()
