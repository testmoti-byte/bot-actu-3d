#!/usr/bin/env python3
"""
Blender Oracle - Version Complète avec Assemblage FFmpeg
Orchestre le rendu Blender headless et assemble la vidéo finale

Fonctionnalités:
- Trouve Blender automatiquement
- Lance le rendu en headless
- Assemble les frames PNG en vidéo MP4 avec ffmpeg
- Génère un nom de fichier unique avec date/heure
"""

import os
import sys
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlenderOracle:
    """Orchestre le rendu Blender complet"""
    
    def __init__(self):
        """Initialise Blender Oracle"""
        self.blender_path = self._find_blender()
        self.ffmpeg_path = self._find_ffmpeg()
        
        # Chemins possibles pour le fichier .blend (recherche dans l'ordre)
        self.possible_blend_paths = [
            "blender/jt_test.blend",
            "mkdir - p blender/jt_test.blend",  # Dossier avec nom bizarre
            "jt_test.blend",
            "../blender/jt_test.blend",
            "../mkdir - p blender/jt_test.blend",
        ]
        
        # Trouve le premier chemin qui existe
        self.project_file = None
        for path in self.possible_blend_paths:
            if os.path.exists(path):
                self.project_file = os.path.abspath(path)
                logger.info(f"✅ Fichier .blend trouvé: {path}")
                break
        
        if not self.project_file:
            self.project_file = "blender/jt_test.blend"
            logger.warning(f"⚠️ Fichier .blend non trouvé, utilisera: {self.project_file}")
        
        # Chemin du script Blender
        self.blender_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "blender_script.py"
        )
        
        logger.info("⭐ BLENDER ORACLE INITIALIZED")
        logger.info(f"   Blender: {self.blender_path}")
        logger.info(f"   FFmpeg: {self.ffmpeg_path}")
        logger.info(f"   Project: {self.project_file}")
        logger.info(f"   Script: {self.blender_script}")
    
    def _find_blender(self):
        """Trouve l'exécutable Blender"""
        # D'abord vérifier la variable d'environnement
        env_path = os.environ.get("BLENDER_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Chercher dans PATH
        blender = shutil.which("blender")
        if blender:
            return blender
        
        # Chemins Windows courants
        windows_paths = [
            "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe",
        ]
        
        for path in windows_paths:
            if os.path.exists(path):
                return path
        
        # Chemins Linux/Mac
        unix_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender",
        ]
        
        for path in unix_paths:
            if os.path.exists(path):
                return path
        
        return "blender"  # Fallback
    
    def _find_ffmpeg(self):
        """Trouve l'exécutable FFmpeg"""
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg
        
        # Chemins Windows courants
        windows_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
        ]
        
        for path in windows_paths:
            if os.path.exists(path):
                return path
        
        return "ffmpeg"  # Fallback
    
    def _generate_output_filename(self, base_name="jt_output"):
        """Génère un nom de fichier unique avec date/heure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.mp4"
    
    def render_jt(self, script=None, audio_file=None, output_file=None):
        """
        Lance le rendu Blender complet
        
        Args:
            script: Dictionnaire avec durée (optionnel)
            audio_file: Chemin vers le fichier audio (optionnel)
            output_file: Chemin de sortie (optionnel, auto-généré si non fourni)
        
        Returns:
            Chemin du fichier vidéo généré
        """
        logger.info("🎬 BLENDER ORACLE - DÉBUT DU RENDU")
        
        # Générer le nom de fichier de sortie
        if not output_file:
            output_filename = self._generate_output_filename()
            output_file = os.path.join("renders", output_filename)
        
        # Créer le dossier de sortie
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Chemin absolu pour le script
        if not os.path.isabs(output_file):
            output_file = os.path.abspath(output_file)
        
        logger.info(f"   Sortie: {output_file}")
        
        # Vérifier que le fichier .blend existe
        if not os.path.exists(self.project_file):
            logger.error(f"❌ Fichier .blend non trouvé: {self.project_file}")
            return None
        
        # Vérifier que le script Blender existe
        if not os.path.exists(self.blender_script):
            logger.error(f"❌ Script Blender non trouvé: {self.blender_script}")
            return None
        
        # Préparer les variables d'environnement
        env = os.environ.copy()
        if audio_file:
            env["JT_AUDIO_FILE"] = os.path.abspath(audio_file)
        env["JT_OUTPUT_FILE"] = output_file
        
        # Construire la commande Blender
        cmd = [
            self.blender_path,
            "--background",           # Mode headless
            "--factory-startup",      # Reset aux settings par défaut
            "-noaudio",               # Pas d'audio au démarrage (on l'ajoute après)
            self.project_file,        # Fichier .blend
            "--python", self.blender_script,  # Script à exécuter
        ]
        
        logger.info(f"🔧 Commande: {' '.join(cmd[:5])}...")
        
        try:
            # Exécuter Blender
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=1800,  # 30 minutes max
                env=env,
                cwd=os.path.dirname(self.project_file) or os.getcwd()
            )
            
            # Logger la sortie
            if result.stdout:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
                for line in stdout_text.split('\n'):
                    if line.strip():
                        logger.info(f"   [Blender] {line}")
            
            if result.stderr:
                stderr_text = result.stderr.decode('utf-8', errors='replace')
                for line in stderr_text.split('\n'):
                    if line.strip() and not 'Warning' in line:
                        logger.warning(f"   [Blender] {line}")
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Blender retour code: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout: Le rendu a pris plus de 30 minutes")
            return None
        except FileNotFoundError:
            logger.error(f"❌ Blender non trouvé: {self.blender_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return None
        
        # Vérifier si la vidéo a été créée directement
        if os.path.exists(output_file):
            logger.info(f"✅ Vidéo créée: {output_file}")
            return output_file
        
        # Sinon, chercher les frames PNG et assembler avec ffmpeg
        frames_dir = os.path.dirname(output_file)
        frames_pattern = os.path.join(frames_dir, "jt_output_frame_*.png")
        
        import glob
        frames = sorted(glob.glob(frames_pattern))
        
        if frames:
            logger.info(f"📦 {len(frames)} frames PNG trouvées, assemblage avec ffmpeg...")
            return self._assemble_video(frames, output_file, audio_file)
        
        logger.error("❌ Aucune sortie trouvée (ni vidéo ni frames)")
        return None
    
    def _assemble_video(self, frames, output_file, audio_file=None):
        """
        Assemble les frames PNG en vidéo avec ffmpeg
        
        Args:
            frames: Liste des chemins des frames PNG
            output_file: Chemin de sortie pour la vidéo
            audio_file: Chemin vers le fichier audio (optionnel)
        
        Returns:
            Chemin du fichier vidéo généré
        """
        if not frames:
            logger.error("❌ Pas de frames à assembler")
            return None
        
        # Répertoire des frames
        frames_dir = os.path.dirname(frames[0])
        
        # Pattern pour ffmpeg
        frames_input = os.path.join(frames_dir, "jt_output_frame_%04d.png")
        
        # Commande ffmpeg de base
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite
            "-framerate", "30",
            "-i", frames_input,
        ]
        
        # Ajouter l'audio si disponible
        if audio_file and os.path.exists(audio_file):
            cmd.extend(["-i", audio_file])
            # Mapper les flux
            cmd.extend([
                "-map", "0:v",  # Vidéo depuis les frames
                "-map", "1:a",  # Audio depuis le fichier audio
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",  # Arrêter quand le plus court finit
            ])
        else:
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
            ])
        
        # Pixel format et sortie
        cmd.extend([
            "-pix_fmt", "yuv420p",
            output_file
        ])
        
        logger.info(f"🔧 Commande ffmpeg: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=600,  # 10 minutes max
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Erreur ffmpeg: {result.stderr}")
                return None
            
            if os.path.exists(output_file):
                logger.info(f"✅ Vidéo assemblée: {output_file}")
                
                # Nettoyer les frames
                self._cleanup_frames(frames)
                
                return output_file
            else:
                logger.error("❌ Vidéo non créée")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout ffmpeg")
            return None
        except FileNotFoundError:
            logger.error(f"❌ ffmpeg non trouvé: {self.ffmpeg_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur assemblage: {e}")
            return None
    
    def _cleanup_frames(self, frames):
        """Supprime les frames PNG après assemblage"""
        logger.info(f"🧹 Nettoyage de {len(frames)} frames...")
        for frame in frames:
            try:
                os.remove(frame)
            except:
                pass


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Blender Oracle - Rendu JT 3D")
    parser.add_argument("--audio", "-a", help="Fichier audio MP3")
    parser.add_argument("--output", "-o", help="Fichier de sortie MP4")
    parser.add_argument("--blend", "-b", help="Fichier .blend (surcharge)")
    
    args = parser.parse_args()
    
    oracle = BlenderOracle()
    
    if args.blend:
        oracle.project_file = args.blend
    
    result = oracle.render_jt(
        audio_file=args.audio,
        output_file=args.output
    )
    
    if result:
        print(f"\n✅ SUCCÈS! Vidéo générée: {result}")
        return 0
    else:
        print(f"\n❌ ÉCHEC du rendu")
        return 1


if __name__ == "__main__":
    sys.exit(main())
