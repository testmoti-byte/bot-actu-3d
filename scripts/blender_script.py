#!/usr/bin/env python3
"""
Blender Script - VERSION CORRIGÉE AXES FBX
S'exécute DANS Blender

Corrections:
- Axes FBX : Forward=-Y, Up=Z (format Mixamo vers Blender)
- Scale armature synchronisé avec mesh
"""

import bpy
import os
import sys
import math
import glob

# ============================================================
# CONFIGURATION
# ============================================================

_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
print(f"📁 Dossier du .blend: {blend_dir}")

ANIMATIONS_DIR = os.path.join(blend_dir, "animations")
AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

FPS = 30
CHAIR_ROTATION = 140

# Position de départ
KARA_START_POS = (-500.0, -800.0, 0.0)
KARA_END_POS = (0.0, 0.0, 0.0)

WALK_DURATION = 2.0
SIT_DURATION = 2.0
CHAIR_TURN_TIME = 0.5

print("=" * 60)
print("🎬 BLENDER SCRIPT - CORRECTION AXES FBX")
print("=" * 60)


def find_kara_file():
    """Trouve le fichier Kara"""
    print(f"\n🔍 Recherche du fichier Kara...")
    
    if not os.path.exists(ANIMATIONS_DIR):
        print(f"   ❌ Dossier non trouvé")
        return None
    
    all_files = os.listdir(ANIMATIONS_DIR)
    fbx_files = [f for f in all_files if f.lower().endswith('.fbx')]
    
    print(f"   📂 Fichiers FBX trouvés:")
    for f in fbx_files:
        print(f"      - {f}")
    
    # Exclure les animations
    anim_kw = ["walking", "sitting", "drinking", "talking", "jog", "excited"]
    
    # Chercher avec "rig" (fichier de base avec squelette)
    for f in fbx_files:
        name_lower = f.lower()
        if "rig" in name_lower and not any(kw in name_lower for kw in anim_kw):
            print(f"   ✅ Trouvé (rig): {f}")
            return os.path.join(ANIMATIONS_DIR, f)
    
    # Chercher Kara.fbx de base
    for f in fbx_files:
        name_lower = f.lower()
        if "kara" in name_lower and not any(kw in name_lower for kw in anim_kw):
            print(f"   ✅ Trouvé: {f}")
            return os.path.join(ANIMATIONS_DIR, f)
    
    # Fallback
    for f in fbx_files:
        if not any(kw in f.lower() for kw in anim_kw):
            print(f"   ⚠️ Fallback: {f}")
            return os.path.join(ANIMATIONS_DIR, f)
    
    if fbx_files:
        print(f"   ⚠️ Premier fichier: {fbx_files[0]}")
        return os.path.join(ANIMATIONS_DIR, fbx_files[0])
    
    return None


def check_files():
    """Vérifie les fichiers"""
    print("\n📂 Vérification...")
    if os.path.exists(ANIMATIONS_DIR):
        for f in sorted(os.listdir(ANIMATIONS_DIR)):
            if f.lower().endswith('.fbx'):
                size = os.path.getsize(os.path.join(ANIMATIONS_DIR, f)) / 1024
                print(f"   - {f} ({size:.0f} KB)")


def clear_scene():
    """Nettoie les anciens objets Kara"""
    print("\n🧹 Nettoyage...")
    for obj in list(bpy.data.objects):
        if "kara" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"   Supprimé: {obj.name}")


def import_kara():
    """Importe Kara avec CORRECTION DES AXES FBX"""
    print(f"\n📥 Import de Kara (correction axes)...")
    
    kara_path = find_kara_file()
    if not kara_path:
        return None, None
    
    try:
        before_objects = set(bpy.data.objects)
        
        # =====================================================
        # CORRECTION DES AXES FBX (MIXAMO → BLENDER)
        # =====================================================
        # Mixamo utilise: Y-up, Z-forward
        # Blender utilise: Z-up, Y-forward
        # Donc on importe avec: Forward=-Y, Up=Z
        
        bpy.ops.import_scene.fbx(
            filepath=kara_path,
            use_anim=True,
            ignore_leaf_bones=False,
            automatic_bone_orientation=True,
            # CORRECTION AXES - CRUCIAL !
            axis_forward='-Y',    # Mixamo: Z forward → Blender: -Y forward
            axis_up='Z',          # Mixamo: Y up → Blender: Z up
            global_scale=1.0,     # Pas de scale automatique
        )
        
        print(f"   ✅ Importé avec axes corrigés (-Y forward, Z up)")
        
        after_objects = set(bpy.data.objects)
        new_objects = after_objects - before_objects
        
        kara_armature = None
        kara_meshes = []
        
        # Analyser les objets importés
        for obj in new_objects:
            print(f"\n   📦 {obj.name} (type: {obj.type})")
            print(f"      📍 Location: {tuple(round(v, 3) for v in obj.location)}")
            print(f"      📏 Scale: {tuple(round(v, 4) for v in obj.scale)}")
            print(f"      🔄 Rotation: {tuple(round(math.degrees(v), 1) for v in obj.rotation_euler)}°")
            
            if obj.type == 'ARMATURE':
                obj.name = "Kara_Armature"
                kara_armature = obj
                print(f"      ✅ Armature détectée")
                
            elif obj.type == 'MESH':
                obj.name = f"Kara_Mesh_{len(kara_meshes)}"
                kara_meshes.append(obj)
                print(f"      ✅ Mesh détecté")
                
                # Afficher les dimensions
                dims = obj.dimensions
                print(f"      📐 Dimensions: {dims[0]:.3f} x {dims[1]:.3f} x {dims[2]:.3f} m")
        
        # =====================================================
        # SYNCHRONISATION SCALE ARMATURE/MESH
        # =====================================================
        if kara_armature and kara_meshes:
            arm_scale = kara_armature.scale[0]
            mesh_scale = kara_meshes[0].scale[0]
            
            if abs(arm_scale - mesh_scale) > 0.01:
                print(f"\n   ⚠️ Scale différent détecté:")
                print(f"      Armature: {arm_scale}")
                print(f"      Mesh: {mesh_scale}")
                
                # Appliquer le scale du mesh à l'armature
                kara_armature.scale = kara_meshes[0].scale
                print(f"      🔧 Armature ajustée au scale du mesh")
                
                # Vérifier le parentage
                for mesh in kara_meshes:
                    if mesh.parent != kara_armature:
                        mesh.parent = kara_armature
                        print(f"      ✅ Parentage corrigé: {mesh.name} → {kara_armature.name}")
        
        # Vérifier l'orientation (rotation)
        if kara_armature:
            rot = kara_armature.rotation_euler
            if abs(rot[0]) > 0.1 or abs(rot[1]) > 0.1:
                print(f"\n   ⚠️ Rotation détectée: le personnage est penché")
                print(f"      Cela peut indiquer un problème d'axes")
        
        # Position de départ
        if kara_armature:
            kara_armature.location = KARA_START_POS
            print(f"\n   📍 Position départ: {KARA_START_POS}")
        
        return kara_armature, kara_meshes[0] if kara_meshes else None
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def find_chair():
    """Trouve la chaise"""
    print(f"\n🪑 Recherche chaise...")
    for obj in bpy.context.scene.objects:
        if any(kw in obj.name.lower() for kw in ["chaise", "chair", "seat"]):
            print(f"   ✅ Trouvée: {obj.name}")
            return obj
    print(f"   ⚠️ Non trouvée")
    return None


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
        print(f"   ✅ Audio ajouté")
    except Exception as e:
        print(f"   ⚠️ Erreur audio: {e}")


def create_animation(kara_armature, chair, total_frames):
    if not kara_armature:
        return
    
    print(f"\n🎭 Création animation...")
    
    walk_end = int(WALK_DURATION * FPS)
    sit_end = walk_end + int(SIT_DURATION * FPS)
    
    # Animation de position
    kara_armature.location = KARA_START_POS
    kara_armature.keyframe_insert(data_path="location", frame=1)
    kara_armature.location = KARA_END_POS
    kara_armature.keyframe_insert(data_path="location", frame=walk_end)
    
    print(f"   ✅ Animation position")
    
    # Rotation chaise
    if chair:
        init_z = chair.rotation_euler[2]
        chair.keyframe_insert(data_path="rotation_euler", frame=sit_end - 1)
        chair.rotation_euler = (chair.rotation_euler[0], chair.rotation_euler[1], 
                                init_z + math.radians(CHAIR_ROTATION))
        chair.keyframe_insert(data_path="rotation_euler", frame=sit_end + int(CHAIR_TURN_TIME * FPS))
        print(f"   ✅ Rotation chaise {CHAIR_ROTATION}°")


def setup_render():
    print(f"\n🎬 Configuration rendu...")
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


def main():
    print("\n" + "=" * 60)
    print("🎬 BLENDER SCRIPT - DÉBUT")
    print("=" * 60)
    
    try:
        check_files()
        clear_scene()
        kara_armature, kara_mesh = import_kara()
        chair = find_chair()
        duration = get_audio_duration()
        frames = setup_timeline(duration)
        create_animation(kara_armature, chair, frames)
        add_audio()
        setup_render()
        
        print(f"\n🎨 Rendu en cours...")
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"   ✅ Terminé!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎬 FIN")
    print("=" * 60)


main()
