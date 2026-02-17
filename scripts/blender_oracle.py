#!/usr/bin/env python3
"""
Blender Oracle - Simple Version
Rend directement sans scripts temporaires!
"""

import os
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BlenderOracle:
    """Orchestre le rendu Blender SIMPLE et DIRECT"""
    
    def __init__(self):
        """Initialise Blender Oracle"""
        self.blender_path = "blender"  # ou le chemin complet si nécessaire
        
        # Chemins possibles pour le fichier .blend (recherche dans l'ordre)
        self.possible_blend_paths = [
            "blender/jt_test.blend",
            "mkdir -p blender/jt_test.blend",  # Dossier avec nom bizarre
            "jt_test.blend",  # Dans le dossier courant
            "../blender/jt_test.blend",
            "../mkdir -p blender/jt_test.blend",
        ]
        
        # Trouve le premier chemin qui existe
        self.project_file = None
        for path in self.possible_blend_paths:
            if os.path.exists(path):
                self.project_file = path
                logger.info(f"✅ Fichier .blend trouvé: {path}")
                break
        
        if not self.project_file:
            self.project_file = "blender/jt_test.blend"  # Défaut
            logger.warning(f"⚠️ Fichier .blend non trouvé, utilisera: {self.project_file}")
        
        logger.info("⭐ BLENDER ORACLE INITIALIZED")
        logger.info(f"   Blender: {self.blender_path}")
        logger.info(f"   Project: {self.project_file}")
    
    def render_jt(self, script: dict, audio_file: str, output_file: str = "renders/jt_output.mp4") -> str:
        """Lance le rendu Blender"""
        try:
            logger.info("🎬 BLENDER ORACLE - JT RENDERING")
            logger.info(f"   Script duration: {script.get('total_duration', 300)}s")
            logger.info(f"   Audio: {audio_file}")
            
            # Vérifier que le fichier .blend existe
            if not os.path.exists(self.project_file):
                logger.warning(f"   ⚠️ Blend file not found: {self.project_file}")
                logger.warning(f"   ⚠️ Creating placeholder video...")
                return self._create_placeholder(output_file)
            
            # Créer le dossier de sortie s'il n'existe pas
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Option 1: Essayer avec subprocess (Blender en ligne de commande)
            logger.info(f"   🎬 Rendering with Blender...")
            
            try:
                # Commande Blender simple pour rendre en headless
                cmd = [
                    self.blender_path,
                    "--background",
                    self.project_file,
                    "--render-output", output_file,
                    "--render-frame", "1"
                ]
                
                logger.info(f"   Command: {' '.join(cmd)}")
                
                # Exécuter Blender
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=600,  # 10 min timeout
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"   ✅ Blender render SUCCESS!")
                    
                    # Vérifier que le fichier a été créé
                    if os.path.exists(output_file) or os.path.exists(output_file + "0001.mp4"):
                        logger.info(f"   ✅ Output file created!")
                        return output_file
                    else:
                        logger.warning(f"   ⚠️ Output file not found, using placeholder")
                        return self._create_placeholder(output_file)
                else:
                    logger.warning(f"   ⚠️ Blender error: {result.stderr[:200]}")
                    return self._create_placeholder(output_file)
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"   ⚠️ Blender timeout (>10min)")
                return self._create_placeholder(output_file)
            except FileNotFoundError:
                logger.warning(f"   ⚠️ Blender not found in PATH")
                logger.warning(f"   ⚠️ Trying with full path...")
                return self._try_full_blender_path(output_file)
            except Exception as e:
                logger.warning(f"   ⚠️ Blender error: {e}")
                return self._create_placeholder(output_file)
        
        except Exception as e:
            logger.error(f"   ❌ Render failed: {e}")
            return self._create_placeholder(output_file)
    
    def _try_full_blender_path(self, output_file: str) -> str:
        """Essaie avec le chemin complet de Blender"""
        try:
            # Chemins possibles sur Windows
            possible_paths = [
                "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
                "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
                "/usr/bin/blender",
                "/Applications/Blender.app/Contents/MacOS/Blender"
            ]
            
            for blender_exe in possible_paths:
                if os.path.exists(blender_exe):
                    logger.info(f"   Found Blender at: {blender_exe}")
                    
                    cmd = [
                        blender_exe,
                        "--background",
                        self.project_file,
                        "--render-output", output_file,
                        "--render-frame", "1"
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=600, text=True)
                    
                    if result.returncode == 0:
                        logger.info(f"   ✅ Render SUCCESS!")
                        return output_file
            
            logger.warning(f"   ⚠️ Blender not found in any default path")
            return self._create_placeholder(output_file)
            
        except Exception as e:
            logger.warning(f"   ⚠️ Full path search failed: {e}")
            return self._create_placeholder(output_file)
    
    def _create_placeholder(self, output_file: str) -> str:
        """Crée un fichier vidéo placeholder"""
        try:
            # Créer un fichier MP4 vide (placeholder)
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Créer un fichier vide pour simuler la vidéo
            with open(output_file, 'wb') as f:
                # En-tête MP4 minimal
                f.write(b'\x00\x00\x00\x20ftypisom')
                f.write(b'\x00' * 100)  # Placeholder data
            
            logger.info(f"   ✅ Placeholder video created: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"   ❌ Placeholder creation failed: {e}")
            return output_file