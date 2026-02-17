#!/usr/bin/env python3
"""
TTS Generator - Utilise Edge TTS (Microsoft)
Transforme le script texte en audio MP3

Avantages :
- Gratuit
- Voix naturelle
- Rapide
"""

import asyncio
import edge_tts
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSGenerator:
    """Générateur de voix avec Edge TTS"""
    
    # Voix françaises disponibles
    FRENCH_VOICES = {
        "denise": "fr-FR-DeniseNeural",      # Voix féminine
        "henri": "fr-FR-HenriNeural",        # Voix masculine
        "alain": "fr-FR-AlainNeural",        # Voix masculine (autre)
        "brigitte": "fr-CA-BrigitteNeural",  # Voix féminine canadienne
        "sylvie": "fr-CA-SylvieNeural",      # Voix féminine canadienne
        "antoine": "fr-CA-AntoineNeural",    # Voix masculine canadienne
    }
    
    def __init__(self, voice: str = "denise"):
        """
        Initialise le générateur TTS
        
        Args:
            voice: Nom de la voix (denise, henri, alain, brigitte, sylvie, antoine)
        """
        self.voice_name = voice.lower()
        self.voice = self.FRENCH_VOICES.get(
            self.voice_name, 
            "fr-FR-DeniseNeural"  # Défaut
        )
        logger.info(f"🔊 TTS Generator initialisé")
        logger.info(f"   Voix: {self.voice_name} ({self.voice})")
    
    async def generate_audio_async(
        self, 
        text: str, 
        output_file: str = "data/audio.mp3"
    ) -> str:
        """
        Génère l'audio de manière asynchrone
        
        Args:
            text: Le texte à convertir en audio
            output_file: Le fichier de sortie
        
        Returns:
            Chemin vers le fichier audio
        """
        logger.info(f"🎵 Génération audio...")
        logger.info(f"   Texte: {len(text)} caractères")
        logger.info(f"   Sortie: {output_file}")
        
        # Créer le dossier si nécessaire
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Créer la communication avec Edge TTS
        communicate = edge_tts.Communicate(text, self.voice)
        
        # Sauvegarder l'audio
        await communicate.save(output_file)
        
        # Vérifier la taille
        file_size = os.path.getsize(output_file) / 1024  # KB
        logger.info(f"✅ Audio généré: {file_size:.1f} KB")
        
        return output_file
    
    def generate_audio(
        self, 
        text: str, 
        output_file: str = "data/audio.mp3"
    ) -> str:
        """
        Génère l'audio (version synchrone pour faciliter l'utilisation)
        
        Args:
            text: Le texte à convertir en audio
            output_file: Le fichier de sortie
        
        Returns:
            Chemin vers le fichier audio
        """
        return asyncio.run(self.generate_audio_async(text, output_file))
    
    def generate_from_script(
        self, 
        script: dict, 
        output_file: str = "data/audio.mp3"
    ) -> str:
        """
        Génère l'audio à partir d'un script structuré
        
        Args:
            script: Le script du JT (avec dialogues, etc.)
            output_file: Le fichier de sortie
        
        Returns:
            Chemin vers le fichier audio
        """
        # Extraire le texte du script
        text = ""
        
        if "dialogues" in script:
            # Format avec dialogues
            for dialogue in script["dialogues"]:
                speaker = dialogue.get("speaker", "")
                content = dialogue.get("content", "")
                text += content + "\n\n"
        elif "content" in script:
            # Format simple
            text = script["content"]
        elif "text" in script:
            # Autre format simple
            text = script["text"]
        else:
            # Le script est peut-être juste le texte
            text = str(script)
        
        return self.generate_audio(text, output_file)
    
    def list_voices(self):
        """Affiche la liste des voix disponibles"""
        print("\n🎤 Voix françaises disponibles :")
        print("-" * 40)
        for name, voice_id in self.FRENCH_VOICES.items():
            print(f"   {name:15} → {voice_id}")
        print("-" * 40)


# ============================================================
# TEST
# ============================================================

def test_tts():
    """Test le générateur TTS"""
    
    # Créer le générateur avec la voix de Denise
    tts = TTSGenerator(voice="denise")
    
    # Texte de test
    test_text = """
    Bonjour et bienvenue dans ce journal télévisé consacré à l'impression 3D.
    
    Aujourd'hui, nous allons parler des dernières innovations dans le monde de la fabrication additive.
    
    Restez avec nous pour découvrir les actualités du jour.
    """
    
    # Générer l'audio
    output = tts.generate_audio(test_text, "data/test_jt.mp3")
    
    print(f"\n✅ Test terminé: {output}")


if __name__ == "__main__":
    test_tts()
