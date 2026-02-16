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
    """Génère les scripts JT avec Gemini"""
    
    def __init__(self, api_key: str = None):
        """Initialise Gemini"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("✅ Gemini initialized")
    
    def generate_jt_script(self, extracted_info: Dict, duration: int = 300) -> Dict:
        """Génère un script JT complet (duration en secondes)"""
        
        logger.info(f"✍️ Generating JT script ({duration}s)...")
        
        prompt = f"""Create a TV news script for "JT 3D PRINTING NEWS".

EXTRACTED INFORMATION:
Title: {extracted_info['title']}
Summary: {extracted_info['summary']}
Keywords: {', '.join(extracted_info['keywords'])}

CHARACTERS:
- Kate Vitali (34, presenter): confident, professional
- Léa Padopoulos (26, co-host): spontaneous, creates humor
- They are friends and work together

REQUIREMENTS:
- Duration: ~{duration//60}min (approximately {duration} seconds of dialogue)
- Format: TV news casual but professional
- Include interaction between Kate and Léa
- Add humor naturally
- Include animations tags like [ANIMATION: action_name]
- Include screen overlay tags like [SCREEN_BLUE: content]

Generate dialogue in French (natural, conversational tone).
Include timing markers at key points.

Format as JSON with structure:
{{
  "opening": {{"speaker": "Kate", "text": "...", "duration": 10, "animation": "..."}},
  "segments": [
    {{"speaker": "...", "text": "...", "duration": ..., "animation": "...", "screen_blue": "..."}},
  ],
  "closing": {{"speaker": "Léa", "text": "...", "duration": 10, "animation": "..."}},
  "total_duration": {duration},
  "animations_needed": ["walk_to_chair", "sit_down", "idle_sitting", ...]
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            
            # Parse JSON from response
            script = self._parse_script_response(script_text)
            logger.info(f"✅ Script generated ({script.get('total_duration', 0)}s)")
            
            return script
            
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return self._default_script(extracted_info, duration)
    
    def generate_series_episode(self, episode_info: Dict, duration: int = 600) -> Dict:
        """Génère un épisode de mini-série (~10 min)"""
        
        logger.info(f"🎬 Generating series episode ({duration//60}min)...")
        
        prompt = f"""Create a mini-series episode script about 3D printing.

EPISODE INFO:
Title: {episode_info.get('title', 'Episode')}
Plot: {episode_info.get('plot', '')}
Genre: {episode_info.get('genre', 'Adventure')}

CHARACTERS:
- Kate: confident, leader
- Léa: creative, humorous

REQUIREMENTS:
- Duration: ~{duration//60}min ({duration} seconds)
- Structure: Setup → Conflict → Resolution
- Include dialogue and action
- Professional but entertaining
- Use [ANIMATION: action] tags
- Use [SCREEN_BLUE: content] for visual elements

Generate full episode script in French.
Format as JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            script = self._parse_script_response(script_text)
            return script
        except Exception as e:
            logger.error(f"❌ Series generation failed: {e}")
            return self._default_series_script(duration)
    
    def generate_film(self, film_info: Dict, duration: int = 7200) -> Dict:
        """Génère un film (~120 min)"""
        
        logger.info(f"🎥 Generating film ({duration//3600}h)...")
        
        prompt = f"""Create a feature film script about 3D printing.

FILM INFO:
Title: {film_info.get('title', 'Untitled')}
Logline: {film_info.get('logline', '')}
Genre: {film_info.get('genre', 'Sci-Fi')}

STRUCTURE:
- Act 1 (Setup): Introduce world and characters
- Act 2A (Rising action): Develop conflict
- Act 2B (Midpoint): Major reveal
- Act 3 (Climax): Resolution

CHARACTERS:
- Kate: leader, resourceful
- Léa: creative problem-solver
- Other roles as needed

Generate full film script in French.
Duration: ~{duration//3600}h
Format as JSON with acts."""
        
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            script = self._parse_script_response(script_text)
            return script
        except Exception as e:
            logger.error(f"❌ Film generation failed: {e}")
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
