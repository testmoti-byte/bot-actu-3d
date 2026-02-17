#!/usr/bin/env python3
"""
Blender Oracle - Le chef d'orchestre
Lance Blender en mode headless (sans interface) avec le script de rendu

Fonctionnalités :
- Trouve Blender automatiquement
- Calcule les paramètres nécessaires
- Lance le rendu en arrière-plan
- Gère les erreurs
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlenderOracle:
    """
    Orchestre le rendu Blender automatique
    Travaille en tandem avec blender_script.py
    """
    
    def __init__(self, project_root: str = None):
        """
        Initialise Blender Oracle
        
        Args:
            project_root: Dossier racine du projet (optionnel)
        """
        self.project_root = project_root or os.getcwd()
        
        # Trouver Blender
        self.blender_path = self._find_blender()
        
        # Trouver le fichier .blend
        self.blend_file = self._find_blend_file()
        
        # Trouver le script Blender
        self.blender_script = self._find_blender_script()
        
        logger.info("=" * 50)
        logger.info("⭐ BLENDER ORACLE INITIALIZED")
        logger.info(f"   Blender: {self.blender_path}")
        logger.info(f"   Projet .blend: {self.blend_file}")
        logger.info(f"   Script: {self.blender_script}")
        logger.info("=" * 50)
    
    def _find_blender(self) -> str:
        """Trouve l'exécutable Blender"""
        
        import platform
        is_windows = platform.system() == "Windows"
        
        # Chemins possibles
        possible_paths = [
            # Windows (le plus probable en premier)
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe",
            
            # Linux
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/opt/blender/blender",
            "/snap/bin/blender",
            
            # macOS
            "/Applications/Blender.app/Contents/MacOS/Blender",
        ]
        
        # Essayer de trouver Blender dans le PATH
        try:
            if is_windows:
                # Sur Windows, utiliser 'where'
                result = subprocess.run(
                    ["where", "blender"], 
                    capture_output=True, 
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Sur Linux/Mac, utiliser 'which'
                result = subprocess.run(
                    ["which", "blender"], 
                    capture_output=True, 
                    text=True
                )
            
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]  # Premier résultat
                logger.info(f"✅ Blender trouvé dans PATH: {path}")
                return path
        except Exception:
            pass  # Ignorer les erreurs et continuer
        
        # Chercher dans les chemins connus
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ Blender trouvé: {path}")
                return path
        
        # Par défaut, utiliser "blender" et croiser les doigts
        logger.warning("⚠️ Blender non trouvé automatiquement")
        logger.warning("⚠️ Veuillez spécifier le chemin manuellement dans le script")
        return "blender"
    
    def _find_blend_file(self) -> str:
        """Trouve le fichier .blend du projet"""
        
        # Chemins possibles
        possible_paths = [
            os.path.join(self.project_root, "blender", "jt_test.blend"),
            os.path.join(self.project_root, "jt_test.blend"),
            os.path.join(self.project_root, "blender", "jt_studio.blend"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ Fichier .blend trouvé: {path}")
                return path
        
        # Par défaut
        default_path = os.path.join(self.project_root, "blender", "jt_test.blend")
        logger.warning(f"⚠️ Fichier .blend non trouvé, utilisation: {default_path}")
        return default_path
    
    def _find_blender_script(self) -> str:
        """Trouve le script Python à exécuter dans Blender"""
        
        possible_paths = [
            os.path.join(self.project_root, "scripts", "blender_script.py"),
            os.path.join(self.project_root, "blender_script.py"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Par défaut
        return os.path.join(self.project_root, "scripts", "blender_script.py")
    
    def _generate_unique_filename(self, base_dir: str = "renders", prefix: str = "jt") -> str:
        """
        Génère un nom de fichier unique avec la date/heure
        
        Format: jt_2026-02-17_20h30.mp4
        """
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Hh%M")
        
        filename = f"{prefix}_{date_str}_{time_str}.mp4"
        filepath = os.path.join(base_dir, filename)
        
        # Si le fichier existe déjà (même minute), ajouter un numéro
        counter = 1
        while os.path.exists(filepath):
            filename = f"{prefix}_{date_str}_{time_str}_{counter}.mp4"
            filepath = os.path.join(base_dir, filename)
            counter += 1
        
        return filepath
    
    def render_jt(
        self, 
        script: dict, 
        audio_file: str, 
        output_file: str = None  # None = génère automatiquement
    ) -> str:
        """
        Lance le rendu du JT
        
        Args:
            script: Le script du JT (contient durée, dialogues, etc.)
            audio_file: Chemin vers le fichier audio MP3
            output_file: Chemin de sortie pour la vidéo (None = auto avec date)
        
        Returns:
            Chemin vers le fichier vidéo généré
        """
        logger.info("=" * 50)
        logger.info("🎬 BLENDER ORACLE - RENDU JT")
        logger.info("=" * 50)
        
        start_time = datetime.now()
        
        # Générer un nom de fichier unique si non spécifié
        if output_file is None:
            output_file = self._generate_unique_filename()
            logger.info(f"📁 Fichier de sortie auto: {output_file}")
        
        try:
            # Vérifier les fichiers nécessaires
            if not os.path.exists(self.blend_file):
                logger.error(f"❌ Fichier .blend non trouvé: {self.blend_file}")
                return self._create_error_video(output_file, "Blend file not found")
            
            if not os.path.exists(self.blender_script):
                logger.error(f"❌ Script Blender non trouvé: {self.blender_script}")
                return self._create_error_video(output_file, "Blender script not found")
            
            # Créer le dossier de sortie
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Préparer la commande Blender
            cmd = [
                self.blender_path,
                "--background",           # Mode sans interface
                "--factory-startup",      # Config par défaut (évite conflits)
                self.blend_file,          # Le fichier .blend
                "--python",               # Exécuter un script Python
                self.blender_script,      # Le script à exécuter
            ]
            
            # Passer des paramètres au script via variables d'environnement
            env = os.environ.copy()
            env["JT_AUDIO_FILE"] = os.path.abspath(audio_file) if audio_file else ""
            env["JT_OUTPUT_FILE"] = os.path.abspath(output_file)
            env["JT_SCRIPT_JSON"] = str(script) if script else "{}"
            
            logger.info(f"📝 Commande Blender:")
            logger.info(f"   {' '.join(cmd)}")
            logger.info(f"")
            logger.info(f"🎵 Audio: {audio_file}")
            logger.info(f"📁 Sortie: {output_file}")
            logger.info(f"")
            logger.info(f"⏳ Rendu en cours... (patience, ça peut prendre 10-30 min)")
            logger.info(f"")
            
            # Lancer Blender
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=1800,  # 30 minutes max
                cwd=self.project_root
            )
            
            # Analyser le résultat
            if result.returncode == 0:
                logger.info("✅ Blender terminé avec succès !")
                
                # Vérifier que le fichier existe
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"")
                    logger.info(f"🎉 VIDÉO GÉNÉRÉE !")
                    logger.info(f"   Fichier: {output_file}")
                    logger.info(f"   Taille: {file_size:.2f} MB")
                    logger.info(f"   Temps: {duration:.1f} secondes")
                    
                    return output_file
                else:
                    logger.error(f"❌ Fichier de sortie non créé: {output_file}")
                    return self._create_error_video(output_file, "Output not created")
            else:
                logger.error(f"❌ Blender a échoué (code: {result.returncode})")
                logger.error(f"STDERR: {result.stderr[:1000]}")
                return self._create_error_video(output_file, f"Blender error: {result.returncode}")
        
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout: Le rendu a pris plus de 30 minutes")
            return self._create_error_video(output_file, "Render timeout")
        
        except FileNotFoundError:
            logger.error(f"❌ Blender non trouvé: {self.blender_path}")
            return self._create_error_video(output_file, "Blender not found")
        
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            return self._create_error_video(output_file, str(e))
    
    def _create_error_video(self, output_file: str, error_message: str) -> str:
        """
        Crée une vidéo d'erreur minimale
        (pour que le pipeline continue)
        """
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Créer un fichier MP4 minimal
            # Note: Ce n'est pas une vraie vidéo, juste un placeholder
            with open(output_file, 'wb') as f:
                # En-tête MP4 minimal
                f.write(b'\x00\x00\x00\x1cftypisom')
                f.write(b'\x00\x00\x00\x08free')
                f.write(b'\x00' * 1000)
            
            logger.warning(f"⚠️ Vidéo d'erreur créée: {output_file}")
            logger.warning(f"   Raison: {error_message}")
            
            return output_file
        
        except Exception as e:
            logger.error(f"❌ Impossible de créer la vidéo d'erreur: {e}")
            return output_file


# ============================================================
# TEST / UTILISATION
# ============================================================

def test_blender_oracle():
    """Test le Blender Oracle"""
    
    oracle = BlenderOracle()
    
    # Script fictif pour le test
    test_script = {
        "total_duration": 30,
        "title": "Test JT 3D",
        "dialogues": []
    }
    
    # Audio fictif
    test_audio = "data/audio.mp3"
    
    # Lancer le rendu - nom de fichier automatique avec date
    # Exemple: renders/jt_2026-02-17_20h30.mp4
    result = oracle.render_jt(
        script=test_script,
        audio_file=test_audio
        # output_file non spécifié = nom automatique avec date
    )
    
    print(f"\n🎬 Résultat: {result}")


if __name__ == "__main__":
    test_blender_oracle()
