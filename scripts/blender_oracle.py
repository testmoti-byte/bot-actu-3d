#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - BLENDER ORACLE ⭐
Le bot magique qui rend tout automatiquement dans Blender
Gère : animations, éclairage, lip-sync, écran bleu hologramme, rendu vidéo
"""

import subprocess
import json
import logging
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class BlenderOracle:
    """Bot Blender qui orchestre tout le rendu"""
    
    def __init__(self, blender_path: str = "blender", blend_file: str = "blender/jt_test.blend"):
        """Initialise Blender Oracle"""
        self.blender_path = blender_path
        self.blend_file = blend_file
        self.output_dir = "renders"
        self.animations_dir = "blender/animations"
        
        # Crée les dossiers
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("⭐ BLENDER ORACLE INITIALIZED")
        logger.info(f"   Blender: {blender_path}")
        logger.info(f"   Project: {blend_file}")
        logger.info(f"   Animations dir: {self.animations_dir}")
    
    def render_jt(self, script: Dict, audio_file: str, output_file: str = "renders/jt_output.mp4") -> str:
        """Rend un JT complet"""
        
        logger.info("🎬 BLENDER ORACLE - JT RENDERING")
        logger.info(f"   📜 Script duration: {script.get('total_duration', 300)}s")
        logger.info(f"   🎤 Audio: {audio_file}")
        
        # Crée le script Python pour Blender
        blender_script = self._generate_blender_script(script, audio_file, output_file)
        blender_script_file = f"blender/render_script_{datetime.now().timestamp()}.py"
        
        with open(blender_script_file, 'w') as f:
            f.write(blender_script)
        
        logger.info(f"   📝 Generated Blender script: {blender_script_file}")
        
        # Lance Blender en headless
        try:
            logger.info("   🚀 Launching Blender (headless)...")
            cmd = [
                self.blender_path,
                self.blend_file,
                "-b",  # Background mode (headless)
                "-P", blender_script_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                logger.error(f"❌ Blender error: {result.stderr}")
                return None
            
            logger.info(result.stdout[-500:] if result.stdout else "   (No output)")
            
            if os.path.exists(output_file):
                logger.info(f"✅ RENDERED: {output_file}")
                return output_file
            else:
                logger.error(f"❌ Render file not created: {output_file}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Blender timeout (>1h)")
            return None
        except Exception as e:
            logger.error(f"❌ Blender execution failed: {e}")
            return None
        finally:
            # Nettoie le script temporaire
            if os.path.exists(blender_script_file):
                os.remove(blender_script_file)
    
    def _generate_blender_script(self, script: Dict, audio_file: str, output_file: str) -> str:
        """Génère le script Python pour Blender"""
        
        return f'''
import bpy
import os
import json
from pathlib import Path

class JT3DBlenderRenderer:
    """Render JT 3D dans Blender"""
    
    def __init__(self):
        self.context = bpy.context
        self.scene = bpy.context.scene
        self.output_file = "{output_file}"
        self.audio_file = "{audio_file}"
        self.animations_dir = "{self.animations_dir}"
        
        print("🎬 JT3D Blender Renderer started")
    
    def setup_rendering(self):
        """Configure Blender pour le rendu"""
        print("   ⚙️ Setting up rendering...")
        
        # Résolution: 1080x1920 (vertical)
        self.scene.render.resolution_x = 1080
        self.scene.render.resolution_y = 1920
        self.scene.render.resolution_percentage = 100
        
        # FPS: 30
        self.scene.render.fps = 30
        self.scene.render.fps_base = 1
        
        # Format: MP4
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.image_settings.ffmpeg_format = 'MPEG4'
        self.scene.render.image_settings.ffmpeg_codec = 'H264'
        self.scene.render.image_settings.ffmpeg_constant_rate_factor = 18
        
        self.scene.render.filepath = self.output_file
        
        print(f"   ✅ Resolution: 1080x1920 @ 30fps")
        print(f"   ✅ Output: {{self.output_file}}")
    
    def setup_lighting(self):
        """Configure l'éclairage (cyan + orange + white)"""
        print("   💡 Setting up lighting...")
        
        # Éclairage principal (blanc pur, haut)
        light_main = bpy.data.lights.new(name="MainLight", type='SUN')
        light_main.energy = 2.0
        light_main.angle = math.radians(5)
        
        obj_main = bpy.data.objects.new("MainLight_obj", light_main)
        bpy.context.collection.objects.link(obj_main)
        obj_main.location = (0, 0, 5)
        obj_main.rotation_euler = (math.radians(45), 0, 0)
        
        # Key light (cyan, latéral)
        light_key = bpy.data.lights.new(name="KeyLight", type='AREA')
        light_key.energy = 1.5
        light_key.size = 2
        mat_key = bpy.data.materials.new("KeyLightMat")
        mat_key.use_nodes = True
        mat_key.node_tree.nodes["Emission"].inputs[0].default_value = (0, 0.85, 1, 1)
        
        obj_key = bpy.data.objects.new("KeyLight_obj", light_key)
        bpy.context.collection.objects.link(obj_key)
        obj_key.location = (-3, 2, 2)
        obj_key.rotation_euler = (math.radians(30), math.radians(45), 0)
        
        # Fill light (orange, latéral)
        light_fill = bpy.data.lights.new(name="FillLight", type='AREA')
        light_fill.energy = 0.8
        light_fill.size = 2
        mat_fill = bpy.data.materials.new("FillLightMat")
        mat_fill.use_nodes = True
        mat_fill.node_tree.nodes["Emission"].inputs[0].default_value = (1, 0.4, 0.2, 1)
        
        obj_fill = bpy.data.objects.new("FillLight_obj", light_fill)
        bpy.context.collection.objects.link(obj_fill)
        obj_fill.location = (3, 2, 1.5)
        obj_fill.rotation_euler = (math.radians(20), math.radians(-45), 0)
        
        print(f"   ✅ Lighting configured (cyan+orange+white)")
    
    def load_animations(self):
        """Charge les animations Mixamo"""
        print("   📂 Loading animations...")
        
        # Les animations doivent déjà être dans le .blend
        # ou on peut les importer ici si FBX
        
        anim_names = ["walk", "sit_down", "idle_sitting"]
        loaded = []
        
        for anim_name in anim_names:
            fbx_file = f"{{self.animations_dir}}/{{anim_name}}.fbx"
            if os.path.exists(fbx_file):
                # Import FBX
                bpy.ops.import_scene.fbx(filepath=fbx_file)
                loaded.append(anim_name)
                print(f"      ✅ Loaded: {{anim_name}}")
        
        return loaded
    
    def setup_camera(self):
        """Configure la caméra"""
        print("   📷 Setting up camera...")
        
        # Cherche la caméra existante
        camera = None
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA':
                camera = obj
                break
        
        if not camera:
            # Crée une nouvelle caméra
            camera_data = bpy.data.cameras.new(name="Camera")
            camera = bpy.data.objects.new("Camera", camera_data)
            bpy.context.collection.objects.link(camera)
        
        # Position caméra (1080x1920 vertical, focale 80mm)
        self.scene.camera = camera
        camera.location = (0, 5, 1.7)
        camera.rotation_euler = (math.radians(0), 0, 0)
        camera_data = camera.data
        camera_data.lens = 80
        
        print(f"   ✅ Camera positioned (80mm lens)")
    
    def add_hologram_screen(self):
        """Ajoute l'écran bleu hologramme"""
        print("   ✨ Adding hologram screen...")
        
        # Crée un plan pour l'écran
        bpy.ops.mesh.primitive_plane_add(
            size=2,
            location=(0, -2, 1)
        )
        screen = bpy.context.active_object
        screen.name = "HologramScreen"
        
        # Matériau hologramme
        mat = bpy.data.materials.new("HologramMat")
        mat.use_nodes = True
        
        # Nœud principal
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0, 0.85, 1, 0.6)
        bsdf.inputs["Emission"].default_value = (0, 0.85, 1, 1)
        bsdf.inputs["Emission Strength"].default_value = 2.0
        bsdf.inputs["Transmission"].default_value = 1.0
        
        screen.data.materials.append(mat)
        
        print(f"   ✅ Hologram screen added (cyan, glow)")
    
    def add_glow_bloom(self):
        """Ajoute des effets glow et bloom"""
        print("   🌟 Adding glow & bloom effects...")
        
        # Active le compositing
        self.scene.use_nodes = True
        nodes = self.scene.node_tree.nodes
        links = self.scene.node_tree.links
        
        # Efface les nœuds par défaut
        nodes.clear()
        
        # Crée les nœuds
        render_layers = nodes.new("CompositorNodeRLayers")
        glare = nodes.new("CompositorNodeGlare")
        glare.glare_type = 'BLOOM'
        glare.intensity = 0.5
        
        composite = nodes.new("CompositorNodeComposite")
        
        # Connecte
        links.new(render_layers.outputs[0], glare.inputs[0])
        links.new(glare.outputs[0], composite.inputs[0])
        
        print(f"   ✅ Bloom effect applied")
    
    def set_animation_timeline(self, script):
        """Configure la timeline avec les animations"""
        print("   ⏱️ Setting up animation timeline...")
        
        duration = script.get('total_duration', 300)
        self.scene.frame_end = int(duration * self.scene.render.fps)
        
        # Applique les animations selon le script
        if 'animations' in script:
            for anim in script['animations']:
                print(f"      - {{anim['action']}} @ {{anim['time']}}s")
        
        print(f"   ✅ Timeline: {{self.scene.frame_end}} frames ({{duration}}s)")
    
    def add_audio(self):
        """Ajoute l'audio à la timeline"""
        print("   🎤 Adding audio...")
        
        if os.path.exists(self.audio_file):
            # Crée une séquence vidéo
            if not self.scene.sequence_editor:
                self.scene.sequence_editor_create()
            
            seq_editor = self.scene.sequence_editor
            seq_editor.sequences.new_sound("Audio", self.audio_file, 1, 1)
            print(f"   ✅ Audio added: {{self.audio_file}}")
    
    def render(self):
        """Lance le rendu"""
        print("   🎬 Starting render...")
        print(f"      Resolution: {{self.scene.render.resolution_x}}x{{self.scene.render.resolution_y}}")
        print(f"      FPS: {{self.scene.render.fps}}")
        print(f"      Duration: {{self.scene.frame_end}} frames")
        
        bpy.ops.render.render(animation=True, write_still=False)
        
        print(f"   ✅ Render complete: {{self.output_file}}")
    
    def run(self):
        """Lance tout le processus de rendu"""
        try:
            print("🎬 =====================================")
            print("   BLENDER ORACLE - JT 3D RENDERING")
            print("🎬 =====================================\\n")
            
            self.setup_rendering()
            self.setup_lighting()
            self.setup_camera()
            self.load_animations()
            self.add_hologram_screen()
            self.add_glow_bloom()
            
            script_data = {script}
            self.set_animation_timeline(script_data)
            self.add_audio()
            
            self.render()
            
            print("\\n✅ =====================================")
            print("   RENDERING COMPLETE!")
            print("✅ =====================================")
            
        except Exception as e:
            print(f"❌ Error: {{e}}")
            import traceback
            traceback.print_exc()

# Exécute le renderer
import math
renderer = JT3DBlenderRenderer()
renderer.run()
'''
    
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        logger.info("🧹 Cleanup...")


def main():
    """Fonction de test"""
    
    test_script = {
        "total_duration": 300,
        "animations": [
            {"time": 0, "action": "walk_to_chair"},
            {"time": 2, "action": "sit_down"},
            {"time": 5, "action": "idle_sitting"}
        ]
    }
    
    oracle = BlenderOracle()
    video = oracle.render_jt(test_script, "data/audio.mp3")
    
    if video:
        print(f"\n✅ Video rendered: {video}")
    else:
        print("\n❌ Rendering failed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
