#!/usr/bin/env python3
"""
HingeAutoBot - Main Application Entry Point
AI agent for automated Hinge dating app interactions
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from .device_manager import DeviceManager
from .ui_detector import UIDetector
from .text_extractor import TextExtractor
from .profile_analyzer import ProfileAnalyzer
from .interaction_controller import InteractionController
from .config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hinge_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HingeAutoBot:
    """Main Hinge automation bot class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Hinge automation bot"""
        self.config = Config(config_path)
        self.device_manager = None
        self.ui_detector = None
        self.text_extractor = None
        self.profile_analyzer = None
        self.interaction_controller = None
        
        logger.info("HingeAutoBot initialized")
    
    def setup(self) -> bool:
        """Setup all components of the bot"""
        try:
            logger.info("Setting up HingeAutoBot components...")
            
            # Initialize device manager
            self.device_manager = DeviceManager(self.config)
            if not self.device_manager.connect():
                logger.error("Failed to connect to device")
                return False
            
            # Initialize UI detector
            self.ui_detector = UIDetector(self.config)
            
            # Initialize text extractor
            self.text_extractor = TextExtractor(self.config)
            
            # Initialize profile analyzer
            self.profile_analyzer = ProfileAnalyzer(self.config)
            
            # Initialize interaction controller
            self.interaction_controller = InteractionController(
                self.device_manager, 
                self.ui_detector,
                self.text_extractor,
                self.profile_analyzer,
                self.config
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def run(self) -> None:
        """Main bot execution loop"""
        if not self.setup():
            logger.error("Bot setup failed. Exiting.")
            return
        
        logger.info("Starting Hinge automation...")
        
        try:
            while True:
                # Capture current screen
                screenshot_path = self.device_manager.capture_screenshot()
                if not screenshot_path:
                    logger.error("Failed to capture screenshot")
                    time.sleep(5)
                    continue
                
                # Detect if we're on a profile screen
                if self.ui_detector.is_profile_screen(screenshot_path):
                    logger.info("Profile screen detected")
                    
                    # Extract profile text
                    profile_text = self.text_extractor.extract_text(screenshot_path)
                    
                    # Analyze profile and make decision (pass screenshot for AI vision)
                    decision = self.profile_analyzer.analyze_profile(profile_text, screenshot_path)
                    
                    # Execute interaction based on decision
                    self.interaction_controller.execute_decision(decision, screenshot_path)
                    
                else:
                    logger.info("Not on profile screen, waiting...")
                
                # Wait before next iteration
                time.sleep(self.config.get('bot_delay', 3))
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        if self.device_manager:
            self.device_manager.disconnect()
        logger.info("Bot cleanup completed")


def main():
    """Main entry point"""
    try:
        bot = HingeAutoBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
