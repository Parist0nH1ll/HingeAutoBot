"""
Interaction Controller - Handles automated interactions with Hinge
"""

import time
import logging
from typing import Optional, Tuple
from .device_manager import DeviceManager
from .ui_detector import UIDetector
from .text_extractor import TextExtractor
from .profile_analyzer import ProfileAnalyzer, ProfileDecision

logger = logging.getLogger(__name__)


class InteractionController:
    """Controls automated interactions with the Hinge app"""
    
    def __init__(self, device_manager: DeviceManager, ui_detector: UIDetector, 
                 text_extractor: TextExtractor, profile_analyzer: ProfileAnalyzer, config):
        self.device_manager = device_manager
        self.ui_detector = ui_detector
        self.text_extractor = text_extractor
        self.profile_analyzer = profile_analyzer
        self.config = config
        
        # Interaction delays
        self.tap_delay = self.config.get('tap_delay', 1.0)
        self.swipe_delay = self.config.get('swipe_delay', 2.0)
        self.text_delay = self.config.get('text_delay', 0.5)
        
    def execute_decision(self, decision: ProfileDecision, screenshot_path: str) -> bool:
        """Execute the decision made by profile analyzer"""
        try:
            logger.info(f"Executing decision: {decision.action} - {decision.reason}")
            
            if decision.action == 'like':
                return self._like_profile(screenshot_path)
            elif decision.action == 'pass':
                return self._pass_profile(screenshot_path)
            elif decision.action == 'comment':
                return self._comment_on_profile(screenshot_path, decision.comment)
            else:
                logger.warning(f"Unknown action: {decision.action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing decision: {e}")
            return False
    
    def _like_profile(self, screenshot_path: str) -> bool:
        """Like the current profile"""
        try:
            # Find like button
            like_button = self.ui_detector.find_like_button(screenshot_path)
            if not like_button:
                logger.error("Could not find like button")
                return False
            
            # Tap like button
            x, y = like_button
            success = self.device_manager.tap(x, y)
            
            if success:
                logger.info("Profile liked successfully")
                time.sleep(self.tap_delay)
                return True
            else:
                logger.error("Failed to tap like button")
                return False
                
        except Exception as e:
            logger.error(f"Error liking profile: {e}")
            return False
    
    def _pass_profile(self, screenshot_path: str) -> bool:
        """Pass on the current profile"""
        try:
            # Find pass button
            pass_button = self.ui_detector.find_pass_button(screenshot_path)
            if not pass_button:
                logger.error("Could not find pass button")
                return False
            
            # Tap pass button
            x, y = pass_button
            success = self.device_manager.tap(x, y)
            
            if success:
                logger.info("Profile passed successfully")
                time.sleep(self.tap_delay)
                return True
            else:
                logger.error("Failed to tap pass button")
                return False
                
        except Exception as e:
            logger.error(f"Error passing profile: {e}")
            return False
    
    def _comment_on_profile(self, screenshot_path: str, comment: Optional[str] = None) -> bool:
        """Comment on the current profile"""
        try:
            if not comment:
                # Generate comment if not provided
                profile_text = self.text_extractor.extract_text(screenshot_path)
                comment = self.profile_analyzer.generate_comment(profile_text)
            
            logger.info(f"Commenting with: {comment}")
            
            # Find comment button
            comment_button = self.ui_detector.find_comment_button(screenshot_path)
            if not comment_button:
                logger.error("Could not find comment button")
                return False
            
            # Tap comment button
            x, y = comment_button
            success = self.device_manager.tap(x, y)
            if not success:
                logger.error("Failed to tap comment button")
                return False
            
            time.sleep(self.tap_delay)
            
            # Find text input field
            text_input = self.ui_detector.find_text_input(screenshot_path)
            if not text_input:
                logger.error("Could not find text input field")
                return False
            
            # Tap text input field
            x, y = text_input
            success = self.device_manager.tap(x, y)
            if not success:
                logger.error("Failed to tap text input field")
                return False
            
            time.sleep(self.text_delay)
            
            # Input comment text
            success = self.device_manager.input_text(comment)
            if not success:
                logger.error("Failed to input comment text")
                return False
            
            time.sleep(self.text_delay)
            
            # Find and tap send button
            send_button = self.ui_detector.find_send_button(screenshot_path)
            if not send_button:
                logger.error("Could not find send button")
                return False
            
            x, y = send_button
            success = self.device_manager.tap(x, y)
            if not success:
                logger.error("Failed to tap send button")
                return False
            
            logger.info("Comment sent successfully")
            time.sleep(self.tap_delay)
            return True
            
        except Exception as e:
            logger.error(f"Error commenting on profile: {e}")
            return False
    
    def swipe_to_next_profile(self) -> bool:
        """Swipe to the next profile"""
        try:
            # Get screen dimensions
            width, height = self.device_manager.get_screen_dimensions()
            
            # Swipe from right to left (next profile)
            start_x = int(width * 0.8)
            start_y = int(height * 0.5)
            end_x = int(width * 0.2)
            end_y = int(height * 0.5)
            
            success = self.device_manager.swipe(start_x, start_y, end_x, end_y)
            
            if success:
                logger.info("Swiped to next profile")
                time.sleep(self.swipe_delay)
                return True
            else:
                logger.error("Failed to swipe to next profile")
                return False
                
        except Exception as e:
            logger.error(f"Error swiping to next profile: {e}")
            return False
    
    def swipe_to_previous_profile(self) -> bool:
        """Swipe to the previous profile"""
        try:
            # Get screen dimensions
            width, height = self.device_manager.get_screen_dimensions()
            
            # Swipe from left to right (previous profile)
            start_x = int(width * 0.2)
            start_y = int(height * 0.5)
            end_x = int(width * 0.8)
            end_y = int(height * 0.5)
            
            success = self.device_manager.swipe(start_x, start_y, end_x, end_y)
            
            if success:
                logger.info("Swiped to previous profile")
                time.sleep(self.swipe_delay)
                return True
            else:
                logger.error("Failed to swipe to previous profile")
                return False
                
        except Exception as e:
            logger.error(f"Error swiping to previous profile: {e}")
            return False
    
    def handle_popup(self, screenshot_path: str) -> bool:
        """Handle any popups that might appear"""
        try:
            # Check for common popup patterns
            # This is a simplified implementation - in practice, you'd need
            # to detect specific popup types and handle them accordingly
            
            # For now, just tap in the center to dismiss any popup
            width, height = self.device_manager.get_screen_dimensions()
            center_x = width // 2
            center_y = height // 2
            
            success = self.device_manager.tap(center_x, center_y)
            
            if success:
                logger.info("Handled popup")
                time.sleep(self.tap_delay)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error handling popup: {e}")
            return False
    
    def wait_for_app_ready(self, max_wait: int = 10) -> bool:
        """Wait for the app to be ready for interaction"""
        try:
            for i in range(max_wait):
                # Capture screenshot to check app state
                screenshot_path = self.device_manager.capture_screenshot()
                if not screenshot_path:
                    time.sleep(1)
                    continue
                
                # Check if we're on a profile screen
                if self.ui_detector.is_profile_screen(screenshot_path):
                    logger.info("App is ready for interaction")
                    return True
                
                time.sleep(1)
            
            logger.warning("App did not become ready within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for app ready: {e}")
            return False
    
    def get_interaction_stats(self) -> dict:
        """Get statistics about interactions"""
        # This would track interaction statistics
        # For now, return empty dict
        return {
            'profiles_liked': 0,
            'profiles_passed': 0,
            'comments_sent': 0,
            'total_interactions': 0
        }
