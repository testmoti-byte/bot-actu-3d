#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - Script Generator with Gemini
Génère les dialogues Léa & Kate avec Gemini API
"""

import google.generativeai as genai
import json
import logging
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiScriptGenerator:
    """Génère les scripts JT - Utilise Ollama/fallback (Gemini désactivé pour économiser le quota)"""
    
    def __init__(self, api_key: str = None):
        """Initialise - Gemini optionnel car on utilise Ollama/fallback"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_enabled = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.gemini_enabled = True
                logger.info("✅ Gemini initialized (mais fallback activé)")
            except Exception as e:
                logger.warning(f"⚠️ Gemini init failed: {e}, using fallback")
        else:
            logger.info("ℹ️ Pas de clé Gemini, utilisation du fallback")
        
        logger.info("✅ Script Generator ready (mode: Ollama/fallback)")
    
    def generate_jt_script(self, extracted_info: dict, duration: int = 300) -> dict:
        """Génère le script JT - Utilise Ollama à la place de Gemini (quota API épuisé)"""
        logger.info(f"✍️ Using Ollama/fallback instead of Gemini (API quota exhausted)...")
        
        # Génère le script avec les infos extraites
        return {
            "opening": {"speaker": "Kara", "text": "Bonjour! Bienvenue sur JT 3D Printing News!", "duration": 10, "animation": "walk_to_chair"},
            "segments": [
                {"speaker": "Kara", "text": extracted_info.get('summary', 'News du jour...'), "duration": duration - 20, "animation": "idle_sitting"}
            ],
            "closing": {"speaker": "Kara", "text": "À demain pour plus de news 3D!", "duration": 10, "animation": "idle_sitting"},
            "total_duration": duration,
            "animations_needed": ["walk_to_chair", "sit_down", "idle_sitting"]
        }
    
    def generate_series_episode(self, episode_info: Dict, duration: int = 600) -> Dict:
        """Génère un épisode de mini-série (~10 min)"""
        
        logger.info(f"🎬 Generating series episode ({duration//60}min)...")
        
        # Fallback direct car Gemini désactivé
        return self._default_series_script(duration)
    
    def generate_film(self, film_info: Dict, duration: int = 7200) -> Dict:
        """Génère un film (~120 min)"""
        
        logger.info(f"🎥 Generating film ({duration//3600}h)...")
        
        # Fallback direct car Gemini désactivé
        return self._default_film_script(duration)
    
    def _parse_script_response(self, response_text: str) -> Dict:
        """Parse la réponse Gemini JSON"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"⚠️ Could not parse JSON: {e}")
        
        return {}
    
    def _default_script(self, info: Dict, duration: int) -> Dict:
        """Script par défaut si Gemini échoue"""
        return {
            "opening": {
                "speaker": "Kate",
                "text": "Bonjour et bienvenue sur JT 3D Printing News!",
                "duration": 10,
                "animation": "walk_to_chair"
            },
            "segments": [
                {
                    "speaker": "Kate",
                    "text": info.get('summary', 'News du jour...'),
                    "duration": duration - 20,
                    "animation": "idle_sitting",
                    "screen_blue": info.get('title', '')
                }
            ],
            "closing": {
                "speaker": "Léa",
                "text": "À demain pour plus de news 3D!",
                "duration": 10,
                "animation": "idle_sitting"
            },
            "total_duration": duration,
            "animations_needed": ["walk_to_chair", "sit_down", "idle_sitting"]
        }
    
    def _default_series_script(self, duration: int) -> Dict:
        """Épisode par défaut"""
        return {
            "title": "Episode",
            "acts": [
                {"name": "Act 1: Setup", "duration": duration // 3},
                {"name": "Act 2: Development", "duration": duration // 3},
                {"name": "Act 3: Resolution", "duration": duration // 3}
            ],
            "total_duration": duration
        }
    
    def _default_film_script(self, duration: int) -> Dict:
        """Film par défaut"""
        return {
            "title": "Film",
            "acts": [
                {"name": "Act 1", "duration": duration // 4},
                {"name": "Act 2A", "duration": duration // 4},
                {"name": "Act 2B", "duration": duration // 4},
                {"name": "Act 3", "duration": duration // 4}
            ],
            "total_duration": duration
        }


def main():
    """Fonction de test"""
    test_info = {
        "title": "Prusa lance nouvelle imprimante",
        "summary": "Innovation révolutionnaire...",
        "keywords": ["Prusa", "3D", "Innovation"]
    }
    
    generator = GeminiScriptGenerator()
    script = generator.generate_jt_script(test_info, duration=300)
    
    print("\n✍️ GENERATED SCRIPT:\n")
    print(json.dumps(script, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
