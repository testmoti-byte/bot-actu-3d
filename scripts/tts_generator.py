#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - TTS Generator
Génère l'audio avec Google Cloud Text-to-Speech (Léa & Kate)
"""

from google.cloud import texttospeech
import json
import logging
import os
from typing import Dict, List
from pydub import AudioSegment
import io
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class JT3DTTSGenerator:
    """Génère l'audio TTS pour JT 3D avec Google Cloud"""
    
    def __init__(self, credentials_path: str = None):
        """Initialise Google TTS"""
        credentials_path = credentials_path or os.getenv("GOOGLE_TTS_CREDENTIALS_FILE")
        self.client = None
        self.gcloud_enabled = False
        
        if credentials_path and os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.gcloud_enabled = True
            logger.info("✅ Google TTS initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google TTS init failed: {e}")
            logger.info("ℹ️ Using fallback TTS mode")
        
        # Voix pour les personnages
        self.voices = {
            "Kate": texttospeech.VoiceSelectionParams(
                language_code="fr-FR",
                name="fr-FR-Neural2-C",  # Voix grave, mature
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            ) if self.gcloud_enabled else None,
            "Léa": texttospeech.VoiceSelectionParams(
                language_code="fr-FR",
                name="fr-FR-Neural2-A",  # Voix jeune, dynamique
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            ) if self.gcloud_enabled else None
        }
        
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=24000,
            speaking_rate=1.0
        ) if self.gcloud_enabled else None
    
    def generate_from_script(self, script: Dict, output_file: str = "data/audio.mp3") -> str:
        """Génère l'audio complet depuis le script"""
        
        logger.info(f"🎤 Generating TTS from script...")
        
        # Si Google Cloud non disponible, créer un fichier fallback
        if not self.gcloud_enabled:
            logger.warning("⚠️ Google Cloud TTS non disponible, création d'un fichier audio fallback")
            return self._create_fallback_audio(script, output_file)
        
        audio_segments = []
        
        # Opening
        if "opening" in script:
            segment = self._generate_segment(script["opening"])
            if segment:
                audio_segments.append(segment)
        
        # Segments
        if "segments" in script:
            for seg in script["segments"]:
                segment = self._generate_segment(seg)
                if segment:
                    audio_segments.append(segment)
        
        # Closing
        if "closing" in script:
            segment = self._generate_segment(script["closing"])
            if segment:
                audio_segments.append(segment)
        
        # Combine tous les segments
        if audio_segments:
            combined = self._combine_audio_segments(audio_segments)
            self._save_audio(combined, output_file)
            logger.info(f"✅ TTS generated: {output_file}")
            return output_file
        else:
            logger.error("❌ No audio segments generated")
            return None
    
    def _create_fallback_audio(self, script: Dict, output_file: str) -> str:
        """Crée un fichier audio de fallback quand Google Cloud n'est pas disponible"""
        try:
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            
            # Calculer la durée approximative du script
            total_duration = script.get("total_duration", 60)
            
            # Créer un silence de la bonne durée
            silence = AudioSegment.silent(duration=total_duration * 1000)
            
            # Sauvegarder
            silence.export(output_file, format="mp3")
            logger.info(f"✅ Fallback audio created: {output_file} ({total_duration}s)")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Fallback audio creation failed: {e}")
            # Créer un fichier vide
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(b'')
            return output_file
    
    def _generate_segment(self, segment_info: Dict) -> AudioSegment:
        """Génère un segment audio"""
        
        try:
            speaker = segment_info.get("speaker", "Kate")
            text = segment_info.get("text", "")
            
            if not text:
                return None
            
            logger.info(f"   🎤 {speaker}: {text[:50]}...")
            
            # Crée la synthèse
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voices.get(speaker, self.voices["Kate"]),
                audio_config=self.audio_config
            )
            
            # Convertit en AudioSegment
            audio = AudioSegment.from_mp3(io.BytesIO(response.audio_content))
            return audio
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed for {speaker}: {e}")
            return None
    
    def _combine_audio_segments(self, segments: List[AudioSegment]) -> AudioSegment:
        """Combine les segments audio"""
        
        logger.info(f"   🔗 Combining {len(segments)} audio segments...")
        
        if not segments:
            return AudioSegment.silent(duration=1000)
        
        # Start avec le premier segment
        combined = segments[0]
        
        # Ajoute les autres avec un petit délai
        for segment in segments[1:]:
            # Ajoute 200ms de silence entre les segments
            silence = AudioSegment.silent(duration=200)
            combined += silence + segment
        
        return combined
    
    def _save_audio(self, audio: AudioSegment, output_file: str):
        """Sauvegarde l'audio en fichier"""
        
        # Crée le dossier s'il n'existe pas
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        
        audio.export(output_file, format="mp3", bitrate="128k")
        logger.info(f"   💾 Audio saved: {output_file}")
    
    def generate_with_timing(self, dialogue_list: List[Dict], output_file: str = "data/audio.mp3") -> Dict:
        """Génère l'audio avec timestamps pour synchronisation"""
        
        logger.info(f"🎤 Generating synchronized TTS...")
        
        timing_data = {
            "segments": [],
            "total_duration": 0,
            "metadata": {}
        }
        
        current_time = 0
        audio_parts = []
        
        for dialogue in dialogue_list:
            speaker = dialogue.get("speaker", "Kate")
            text = dialogue.get("text", "")
            
            if not text:
                continue
            
            try:
                # Génère le segment
                synthesis_input = texttospeech.SynthesisInput(text=text)
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=self.voices.get(speaker, self.voices["Kate"]),
                    audio_config=self.audio_config
                )
                
                audio = AudioSegment.from_mp3(io.BytesIO(response.audio_content))
                duration_ms = len(audio)
                
                # Enregistre le timing
                segment_info = {
                    "speaker": speaker,
                    "text": text[:100],
                    "start": current_time / 1000,
                    "duration": duration_ms / 1000,
                    "end": (current_time + duration_ms) / 1000
                }
                timing_data["segments"].append(segment_info)
                
                # Ajoute le segment
                audio_parts.append(audio)
                silence = AudioSegment.silent(duration=200)
                audio_parts.append(silence)
                
                current_time += duration_ms + 200
                
            except Exception as e:
                logger.error(f"❌ TTS failed for {speaker}: {e}")
        
        # Combine et sauvegarde
        if audio_parts:
            combined = sum(audio_parts[:-1])  # Retire le dernier silence
            self._save_audio(combined, output_file)
            
            timing_data["total_duration"] = len(combined) / 1000
            timing_data["metadata"]["file"] = output_file
            
            logger.info(f"✅ Synchronized TTS generated ({timing_data['total_duration']:.1f}s)")
            
            return timing_data
        
        return timing_data


def main():
    """Fonction de test"""
    
    test_script = {
        "opening": {
            "speaker": "Kate",
            "text": "Bonjour et bienvenue sur JT 3D Printing News!"
        },
        "segments": [
            {
                "speaker": "Kate",
                "text": "Aujourd'hui, nous couvrons l'actualité mondiale de l'impression 3D."
            },
            {
                "speaker": "Léa",
                "text": "Oui, et c'est vraiment cool!"
            }
        ],
        "closing": {
            "speaker": "Léa",
            "text": "À demain pour plus de news!"
        }
    }
    
    generator = JT3DTTSGenerator()
    audio_file = generator.generate_from_script(test_script)
    
    print(f"\n🎤 Audio generated: {audio_file}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
