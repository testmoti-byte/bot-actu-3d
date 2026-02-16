#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - Main Orchestrator
Pipeline complète : scraper → Ollama → Gemini → TTS → Blender → Upload
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JT3DOrchestrator:
    """Orchestre tout le pipeline JT 3D"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialise l'orchestrateur"""
        self.config_path = config_path
        self.config = self._load_config()
        self.start_time = datetime.now()
        logger.info("🎬 JT 3D Orchestrator démarré")
    
    def _load_config(self) -> dict:
        """Charge la configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"✅ Config chargée: {self.config_path}")
                return config
            else:
                logger.warning(f"⚠️ Config file not found: {self.config_path}")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in {self.config_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Erreur config: {e}")
            return {}
    
    def run(self, test_mode: bool = False):
        """Lance le pipeline complet"""
        try:
            logger.info("\n" + "="*50)
            logger.info("🎬 JT 3D PIPELINE DÉMARRÉE")
            logger.info("="*50 + "\n")
            
            # ÉTAPE 1 : SCRAPER
            logger.info("🔍 ÉTAPE 1 : Scraper les news...")
            news = self._scrape_news()
            if not news:
                logger.warning("⚠️ Aucune news trouvée")
                return
            logger.info(f"✅ {len(news)} news trouvées\n")
            
            # ÉTAPE 2 : OLLAMA
            logger.info("📊 ÉTAPE 2 : Extraire infos avec Ollama...")
            extracted = self._extract_with_ollama(news[0])
            logger.info(f"✅ Info extraite: {extracted['title'][:50]}...\n")
            
            # ÉTAPE 3 : GEMINI
            logger.info("📝 ÉTAPE 3 : Générer script avec Gemini...")
            script = self._generate_script_with_gemini(extracted)
            logger.info(f"✅ Script généré ({script.get('duration', 0)}s)\n")
            
            # ÉTAPE 4 : TTS
            logger.info("🎤 ÉTAPE 4 : Générer TTS...")
            audio_file = self._generate_tts(script)
            logger.info(f"✅ Audio généré: {audio_file}\n")
            
            # ÉTAPE 5 : BLENDER
            logger.info("🎬 ÉTAPE 5 : Rendu Blender...")
            video_file = self._render_blender(script, audio_file)
            logger.info(f"✅ Vidéo rendue: {video_file}\n")
            
            # ÉTAPE 6 : UPLOAD
            logger.info("📤 ÉTAPE 6 : Upload vidéo...")
            self._upload_video(video_file)
            logger.info(f"✅ Vidéo uploadée!\n")
            
            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.info("="*50)
            logger.info(f"✅ PIPELINE COMPLÈTE EN {elapsed:.1f}s ! 🎉")
            logger.info("="*50 + "\n")
            
            return video_file
            
        except Exception as e:
            logger.error(f"\n❌ Erreur pipeline: {e}", exc_info=True)
            raise
    
    def _scrape_news(self) -> list:
        """Scrape les news"""
        logger.info("   📡 Scraping RSS feeds...")
        # Placeholder - news de test
        return [
            {
                "title": "Prusa lance nouvelle imprimante révolutionnaire",
                "content": "Prusa vient de dévoiler une imprimante 3D révolutionnaire avec nouvelles capacités...",
                "source": "3D Printing Industry",
                "date": datetime.now().isoformat()
            }
        ]
    
    def _extract_with_ollama(self, news: dict) -> dict:
        """Extrait infos avec Ollama"""
        logger.info(f"   🤖 Analysant: {news['title'][:50]}...")
        # Placeholder
        return {
            "title": news["title"],
            "summary": "Résumé: Innovation majeure en impression 3D...",
            "angles": {
                "technical": "Amélioration technologique significative",
                "market": "Impact positif sur le marché",
                "business": "Opportunités commerciales"
            },
            "keywords": ["Prusa", "Innovation", "3D Printing"]
        }
    
    def _generate_script_with_gemini(self, extracted: dict) -> dict:
        """Génère script avec Gemini"""
        logger.info("   ✍️ Generating script...")
        # Placeholder
        return {
            "dialogue": [
                {"speaker": "Kara", "text": "Bonjour! Bienvenue sur JT 3D Printing News.", "duration": 5},
                {"speaker": "Kara", "text": extracted["summary"], "duration": 30}
            ],
            "duration": 45
        }
    
    def _generate_tts(self, script: dict) -> str:
        """Génère TTS"""
        logger.info("   🎤 Generating TTS...")
        audio_file = "data/audio.mp3"
        # Placeholder
        return audio_file
    
    def _render_blender(self, script: dict, audio_file: str) -> str:
        """Lance rendu Blender"""
        logger.info("   🎬 Rendering Blender...")
        video_file = "renders/jt_output.mp4"
        # Placeholder
        return video_file
    
    def _upload_video(self, video_file: str):
        """Upload vidéo"""
        logger.info(f"   📤 Uploading {video_file}...")
        # Placeholder
        logger.info("   ✅ Uploaded!")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JT 3D Printing News Orchestrator")
    parser.add_argument("--test", action="store_true", help="Mode test rapide")
    parser.add_argument("--config", default="config.json", help="Fichier config")
    
    args = parser.parse_args()
    
    try:
        orchestrator = JT3DOrchestrator(args.config)
        orchestrator.run(test_mode=args.test)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
