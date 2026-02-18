#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - Ollama News Extractor
Extrait les infos principales avec Ollama (Phi 3.8b par défaut)
"""

import requests
import json
import logging
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OllamaNewsExtractor:
    """Extrait infos d'une news avec Ollama Phi 3.8b"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "phi3:3.8b"):
        """Initialise l'extracteur Ollama"""
        self.host = host
        # Le modèle par défaut est maintenant 'phi3:3.8b'
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:3.8b")
        self.api_url = f"{self.host}/api/generate"
        logger.info(f"🤖 Ollama Extractor initialized ({self.model})")
    
    def extract(self, article: Dict) -> Dict:
        """Extrait les infos principales d'un article"""
        
        logger.info(f"📊 Analyzing: {article['title'][:50]}...")
        
        # Prompt pour extraction
        prompt = f"""Analyze this 3D printing news and extract key information.

Title: {article['title']}
Content: {article['content'][:500]}

Please provide:
1. Brief summary (2-3 sentences)
2. Key technical points (bullet list)
3. Market impact assessment
4. Relevance score (0-10)
5. Keywords (5-7)

Format JSON only."""
        
        try:
            # Timeout augmenté à 300 secondes (5 minutes) pour le disque dur
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=300 
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ollama error: {response.status_code}")
                return self._default_extraction(article)
            
            result = response.json()
            extracted_text = result.get("response", "")
            
            # Parse la réponse
            extracted_info = self._parse_response(extracted_text)
            
            return {
                "title": article["title"],
                "source": article["source"],
                "summary": extracted_info.get("summary", ""),
                "technical_points": extracted_info.get("technical_points", []),
                "market_impact": extracted_info.get("market_impact", ""),
                "relevance_score": extracted_info.get("relevance_score", 5),
                "keywords": extracted_info.get("keywords", []),
                "angles": {
                    "technical": self._generate_angle(article, "technical"),
                    "market": self._generate_angle(article, "market"),
                    "business": self._generate_angle(article, "business")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur Ollama: {e}")
            return self._default_extraction(article)
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse la réponse Ollama"""
        try:
            # Essaye de parser JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback si pas JSON
        return {
            "summary": response_text[:200],
            "technical_points": [],
            "market_impact": "",
            "relevance_score": 5,
            "keywords": []
        }
    
    def _generate_angle(self, article: Dict, angle_type: str) -> str:
        """Génère un angle différent pour l'article"""
        
        if angle_type == "technical":
            return f"Innovation technologique: {article['title']} représente une avancée en impression 3D..."
        elif angle_type == "market":
            return f"Impact marché: Cette annonce affecte le secteur de l'impression 3D avec potentiel de croissance..."
        else:  # business
            return f"Enjeux commerciaux: Pour les entreprises, cette innovation signifie opportunités et défis..."
    
    def _default_extraction(self, article: Dict) -> Dict:
        """Extraction par défaut si Ollama échoue"""
        return {
            "title": article["title"],
            "source": article["source"],
            "summary": article["content"][:200],
            "technical_points": ["Impression 3D", "Innovation"],
            "market_impact": "Impact positif sur le marché",
            "relevance_score": 5,
            "keywords": ["3d printing", "innovation", "technology"],
            "angles": {
                "technical": "Avancée technologique en impression 3D",
                "market": "Impact sur le marché mondial",
                "business": "Opportunités commerciales"
            }
        }


class OllamaLipSyncAnalyzer:
    """Analyse le texte pour générer lip-sync et gestes"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "phi3:3.8b"):
        """Initialise l'analyseur lip-sync"""
        self.host = host
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:3.8b")
        self.api_url = f"{self.host}/api/generate"
    
    def analyze_for_animation(self, script_text: str) -> Dict:
        """Analyse le script pour animations et lip-sync"""
        
        prompt = f"""Analyze this TV script for animations and gestures.

Script: {script_text}

Provide:
1. Emotions detected
2. Suggested gestures (list)
3. Head movements (looking left/right/center)
4. Hand animations (if any)
5. Timing of key moments (in seconds)

Format as JSON."""
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=300 
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_animation_response(result.get("response", ""))
            
        except Exception as e:
            logger.warning(f"⚠️ Ollama animation analysis failed: {e}")
        
        # Fallback
        return {
            "emotions": ["neutral"],
            "gestures": [],
            "head_movements": "center",
            "hand_animations": [],
            "timing": {}
        }
    
    def _parse_animation_response(self, response_text: str) -> Dict:
        """Parse la réponse animation Ollama"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass
        
        return {
            "emotions": ["neutral"],
            "gestures": [],
            "head_movements": "center",
            "hand_animations": [],
            "timing": {}
        }


def main():
    """Fonction de test"""
    test_article = {
        "title": "Prusa lance nouvelle imprimante révolutionnaire",
        "content": "Prusa vient de dévoiler une imprimante 3D révolutionnaire...",
        "source": "3D Printing Industry"
    }
    
    extractor = OllamaNewsExtractor()
    extracted = extractor.extract(test_article)
    
    print("\n📊 EXTRACTED INFO:\n")
    print(json.dumps(extracted, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
