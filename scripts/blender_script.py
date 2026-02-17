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

# ============================================================
# CONFIGURATION
# ============================================================

# Lire les variables d'environnement passées par blender_oracle.py
_audio_file_from_env = os.environ.get("JT_AUDIO_FILE", "")
_output_file_from_env = os.environ.get("JT_OUTPUT_FILE", "")

# Déterminer le dossier de base (là où est le .blend)
blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
print(f"📁 Dossier du .blend: {blend_dir}")

# Chemins absolus (basés sur le dossier du .blend)
KARA_PATH = os.path.join(blend_dir, "animations", "Kara.fbx")
ANIMATIONS_DIR = os.path.join(blend_dir, "animations")

# Fichier audio (utiliser celui de l'environnement ou défaut)
AUDIO_FILE = _audio_file_from_env if _audio_file_from_env else os.path.join(blend_dir, "data", "audio.mp3")

# Fichier de sortie
OUTPUT_FILE = _output_file_from_env if _output_file_from_env else os.path.join(blend_dir, "renders", "jt_output.mp4")

# Configuration
FPS = 30
CAMERA_ZOOM_DURATION = 2.0  # secondes

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
    
    files_ok = True
    
    # Vérifier Kara
    if os.path.exists(KARA_PATH):
        print(f"   ✅ Kara trouvé: {KARA_PATH}")
    else:
        print(f"   ❌ Kara NON trouvé: {KARA_PATH}")
        files_ok = False
    
    # Vérifier le dossier animations
    if os.path.exists(ANIMATIONS_DIR):
        print(f"   ✅ Dossier animations trouvé")
        # Lister les animations disponibles
        for f in os.listdir(ANIMATIONS_DIR):
            if f.endswith('.fbx'):
                print(f"      - {f}")
    else:
        print(f"   ❌ Dossier animations NON trouvé: {ANIMATIONS_DIR}")
        files_ok = False
    
    # Vérifier l'audio
    if os.path.exists(AUDIO_FILE):
        print(f"   ✅ Audio trouvé: {AUDIO_FILE}")
    else:
        print(f"   ⚠️ Audio NON trouvé: {AUDIO_FILE} (on utilisera 30s par défaut)")
    
    return files_ok


def clear_scene():
    """Nettoie Kara si elle existe déjà"""
    print("\n🧹 Nettoyage...")
    
    # Supprimer Kara si elle existe déjà
    for obj in bpy.data.objects:
        if "Kara" in obj.name or "kara" in obj.name.lower():
            bpy.data.objects.remove(obj, do_unlink=True)
            print(f"   Supprimé: {obj.name}")


def import_kara():
    """Importe Kara depuis le fichier FBX"""
    print(f"\n📥 Import de Kara...")
    
    if not os.path.exists(KARA_PATH):
        print(f"   ❌ Fichier non trouvé: {KARA_PATH}")
        return None
    
    try:
        # Sauvegarder les objets avant import
        before = set(bpy.data.objects)
        
        # Importer le FBX
        bpy.ops.import_scene.fbx(filepath=KARA_PATH)
        
        # Trouver les nouveaux objets
        after = set(bpy.data.objects)
        new_objects = after - before
        
        if new_objects:
            # Le personnage est souvent le premier objet importé
            for obj in new_objects:
                if obj.type == 'ARMATURE' or obj.type == 'MESH':
                    obj.name = "Kara"
                    print(f"   ✅ Kara importée: {obj.name}")
                    return obj
        
        print("   ⚠️ Objet non trouvé après import")
        return None
        
    except Exception as e:
        print(f"   ❌ Erreur import: {e}")
        return None


def get_audio_duration():
    """Calcule la durée de l'audio"""
    print(f"\n🎵 Analyse audio...")
    
    if not os.path.exists(AUDIO_FILE):
        print(f"   ⚠️ Audio non trouvé, durée par défaut: 30s")
        return 30.0
    
    try:
        # Essayer avec mutagen (si installé)
        try:
            from mutagen.mp3 import MP3
            audio = MP3(AUDIO_FILE)
            duration = audio.info.length
            print(f"   ✅ Durée audio: {duration:.2f} secondes")
            return duration
        except:
            pass
        
        # Essayer avec wave (pour les WAV)
        try:
            import wave
            with wave.open(AUDIO_FILE, 'r') as audio:
                frames = audio.getnframes()
                rate = audio.getframerate()
                duration = frames / float(rate)
                print(f"   ✅ Durée audio: {duration:.2f} secondes")
                return duration
        except:
            pass
        
        # Si rien ne marche, durée par défaut
        print(f"   ⚠️ Impossible de lire l'audio, durée par défaut: 30s")
        return 30.0
        
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}, durée par défaut: 30s")
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
        print(f"   ⚠️ Audio non trouvé, pas d'audio ajouté")
        return
    
    try:
        # Créer l'éditeur de séquence si nécessaire
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        
        # Supprimer les anciens audios
        for seq in bpy.context.scene.sequence_editor.sequences_all:
            if seq.type == 'SOUND':
                bpy.context.scene.sequence_editor.sequences.remove(seq)
        
        # Ajouter le nouvel audio
        bpy.context.scene.sequence_editor.sequences.new_sound(
            "JT_Audio",
            AUDIO_FILE,
            channel=1,
            frame_start=1
        )
        print(f"   ✅ Audio ajouté à la timeline")
        
    except Exception as e:
        print(f"   ❌ Erreur ajout audio: {e}")


def find_camera():
    """Trouve la caméra de la scène"""
    print(f"\n📹 Recherche caméra...")
    
    # Chercher la caméra active
    camera = bpy.context.scene.camera
    
    if camera:
        print(f"   ✅ Caméra active: {camera.name}")
        return camera
    
    # Chercher n'importe quelle caméra
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            print(f"   ✅ Caméra trouvée: {obj.name}")
            return obj
    
    print(f"   ⚠️ Aucune caméra trouvée")
    return None


def setup_render():
    """Configure les paramètres de rendu"""
    print(f"\n🎬 Configuration rendu...")
    
    # Créer le dossier de sortie si nécessaire
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"   Dossier créé: {output_dir}")
    
    # Format vidéo
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    
    # Résolution
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    # Fichier de sortie
    bpy.context.scene.render.filepath = OUTPUT_FILE
    
    print(f"   Résolution: 1080x1920")
    print(f"   Codec: H264")
    print(f"   Sortie: {OUTPUT_FILE}")


def render():
    """Lance le rendu"""
    print(f"\n🎨 Lancement du rendu...")
    print(f"   ⏳ Patience, ça peut prendre plusieurs minutes...")
    
    try:
        # Rendu de l'animation
        bpy.ops.render.render(animation=True, write_still=True)
        print(f"   ✅ Rendu terminé !")
        
        # Vérifier le fichier
        if os.path.exists(OUTPUT_FILE):
            size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
            print(f"   📁 Fichier: {OUTPUT_FILE}")
            print(f"   📊 Taille: {size:.2f} MB")
        else:
            print(f"   ⚠️ Fichier non créé: {OUTPUT_FILE}")
            
    except Exception as e:
        print(f"   ❌ Erreur rendu: {e}")


# ============================================================
# MAIN
# ============================================================

def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("🎬 BLENDER SCRIPT - DÉBUT")
    print("=" * 60)
    
    try:
        # 1. Vérifier les fichiers
        check_files()
        
        # 2. Nettoyer
        clear_scene()
        
        # 3. Importer Kara
        kara = import_kara()
        
        # 4. Calculer la durée
        duration = get_audio_duration()
        
        # 5. Configurer la timeline
        total_frames = setup_timeline(duration)
        
        # 6. Ajouter l'audio
        add_audio()
        
        # 7. Trouver la caméra
        find_camera()
        
        # 8. Configurer le rendu
        setup_render()
        
        # 9. Lancer le rendu
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
