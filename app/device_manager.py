"""
Device Manager - Handles ADB connection and device operations
"""

import os
import time
import logging
from typing import Optional, Tuple
from ppadb.client import Client as AdbClient
from PIL import Image

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages ADB device connection and operations"""
    
    def __init__(self, config):
        self.config = config
        self.client = None
        self.device = None
        self.screen_width = 0
        self.screen_height = 0
        
    def connect(self) -> bool:
        """Connect to Android device via ADB"""
        try:
            # Initialize ADB client
            self.client = AdbClient(host="127.0.0.1", port=5037)
            
            # Get device list
            devices = self.client.devices()
            
            if not devices:
                logger.error("No devices found. Please ensure:")
                logger.error("1. Device is connected via USB or wireless ADB")
                logger.error("2. USB debugging is enabled")
                logger.error("3. Device is authorized for debugging")
                return False
            
            # Use first available device
            self.device = devices[0]
            logger.info(f"Connected to device: {self.device.serial}")
            
            # Get screen dimensions
            self._get_screen_dimensions()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False
    
    def _get_screen_dimensions(self) -> None:
        """Get device screen dimensions"""
        try:
            # Get screen size using wm size command
            result = self.device.shell("wm size")
            if "Physical size:" in result:
                size_str = result.split("Physical size: ")[1].strip()
                width, height = map(int, size_str.split("x"))
                self.screen_width = width
                self.screen_height = height
                logger.info(f"Screen dimensions: {width}x{height}")
            else:
                # Fallback to default dimensions
                self.screen_width = 1080
                self.screen_height = 1920
                logger.warning("Could not get screen dimensions, using defaults")
                
        except Exception as e:
            logger.error(f"Failed to get screen dimensions: {e}")
            self.screen_width = 1080
            self.screen_height = 1920
    
    def capture_screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Capture screenshot from device"""
        try:
            if not self.device:
                logger.error("Device not connected")
                return None
            
            # Capture screenshot
            screenshot = self.device.screencap()
            
            # Generate filename if not provided
            if not save_path:
                timestamp = int(time.time())
                save_path = f"screenshots/screenshot_{timestamp}.png"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save screenshot
            with open(save_path, "wb") as f:
                f.write(screenshot)
            
            logger.debug(f"Screenshot saved: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def tap(self, x: int, y: int) -> bool:
        """Tap at specified coordinates"""
        try:
            if not self.device:
                logger.error("Device not connected")
                return False
            
            # Ensure coordinates are within screen bounds
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))
            
            self.device.shell(f"input tap {x} {y}")
            logger.debug(f"Tapped at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to tap at ({x}, {y}): {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 300) -> bool:
        """Swipe from start to end coordinates"""
        try:
            if not self.device:
                logger.error("Device not connected")
                return False
            
            # Ensure coordinates are within screen bounds
            start_x = max(0, min(start_x, self.screen_width - 1))
            start_y = max(0, min(start_y, self.screen_height - 1))
            end_x = max(0, min(end_x, self.screen_width - 1))
            end_y = max(0, min(end_y, self.screen_height - 1))
            
            self.device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
            logger.debug(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False
    
    def input_text(self, text: str) -> bool:
        """Input text using keyboard"""
        try:
            if not self.device:
                logger.error("Device not connected")
                return False
            
            # Escape special characters for shell command
            escaped_text = text.replace(" ", "%s").replace("'", "\\'")
            self.device.shell(f"input text '{escaped_text}'")
            logger.debug(f"Input text: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to input text: {e}")
            return False
    
    def press_key(self, keycode: str) -> bool:
        """Press a specific key"""
        try:
            if not self.device:
                logger.error("Device not connected")
                return False
            
            self.device.shell(f"input keyevent {keycode}")
            logger.debug(f"Pressed key: {keycode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key {keycode}: {e}")
            return False
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """Get current screen dimensions"""
        return self.screen_width, self.screen_height
    
    def disconnect(self) -> None:
        """Disconnect from device"""
        if self.device:
            logger.info("Disconnecting from device")
            self.device = None
        if self.client:
            self.client = None
