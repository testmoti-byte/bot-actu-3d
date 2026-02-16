#!/usr/bin/env python3
"""
JT 3D PRINTING NEWS - Telegram Sender
Envoie la vidéo finale sur Telegram
"""

import telegram
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramSender:
    """Envoie les vidéos sur Telegram"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """Initialise le bot Telegram"""
        bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            logger.warning("⚠️ Telegram config incomplete (optional for testing)")
            self.bot = None
            self.chat_id = None
        else:
            self.bot = telegram.Bot(token=bot_token)
            self.chat_id = chat_id
            logger.info("✅ Telegram initialized")
    
    def send_video(self, video_file: str, caption: str = "🎬 JT 3D Printing News") -> bool:
        """Envoie une vidéo"""
        
        if not self.bot or not self.chat_id:
            logger.warning("⚠️ Telegram not configured, skipping send")
            return False
        
        if not os.path.exists(video_file):
            logger.error(f"❌ Video file not found: {video_file}")
            return False
        
        try:
            logger.info(f"📤 Sending video to Telegram: {video_file}")
            
            with open(video_file, 'rb') as f:
                self.bot.send_video(
                    chat_id=self.chat_id,
                    video=f,
                    caption=caption,
                    supports_streaming=True
                )
            
            logger.info("✅ Video sent to Telegram!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Envoie un message"""
        
        if not self.bot or not self.chat_id:
            return False
        
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info(f"✅ Message sent: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Message send failed: {e}")
            return False


def main():
    """Fonction de test"""
    
    sender = TelegramSender()
    
    # Test message
    sender.send_message("🚀 JT 3D Automation test")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
