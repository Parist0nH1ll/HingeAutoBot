"""
UI Detector - AI vision module for detecting UI elements
"""

import base64
import openai
import logging
from typing import Optional, List, Tuple, Dict
from PIL import Image
import io

logger = logging.getLogger(__name__)


class UIDetector:
    """Detects UI elements using AI vision"""
    
    def __init__(self, config):
        self.config = config
        self.openai_client = None
        self._setup_openai()
        
    def _setup_openai(self) -> None:
        """Setup OpenAI client"""
        try:
            api_key = self.config.get('openai_api_key')
            if not api_key:
                logger.error("OpenAI API key not found in configuration")
                return
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized for UI detection")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
    
    def is_profile_screen(self, screenshot_path: str) -> bool:
        """Check if current screen is a profile screen using AI vision"""
        try:
            if not self.openai_client:
                logger.warning("OpenAI client not available, using fallback detection")
                return self._fallback_profile_detection(screenshot_path)
            
            # Encode image to base64
            base64_image = self._encode_image_to_base64(screenshot_path)
            if not base64_image:
                return False
            
            # Create prompt for AI vision
            prompt = """
            Analyze this screenshot from a mobile dating app (likely Hinge). 
            Determine if this is a profile screen showing a person's dating profile.
            
            Look for these indicators:
            - A person's photo(s)
            - Like/Pass buttons (usually heart/X or thumbs up/down)
            - Profile text/bio information
            - Name and age
            - Dating app interface elements
            
            Respond with only "YES" if this is a profile screen, or "NO" if it's not.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            is_profile = result == "YES"
            
            logger.debug(f"AI profile screen detection: {result}")
            return is_profile
            
        except Exception as e:
            logger.error(f"Error in AI profile screen detection: {e}")
            return self._fallback_profile_detection(screenshot_path)
    
    def find_like_button(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """Find the like button coordinates using AI vision"""
        return self._find_button_ai(screenshot_path, 'like')
    
    def find_pass_button(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """Find the pass button coordinates using AI vision"""
        return self._find_button_ai(screenshot_path, 'pass')
    
    def find_comment_button(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """Find the comment button coordinates using AI vision"""
        return self._find_button_ai(screenshot_path, 'comment')
    
    def find_send_button(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """Find the send button coordinates using AI vision"""
        return self._find_button_ai(screenshot_path, 'send')
    
    def find_text_input(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """Find text input field coordinates using AI vision"""
        return self._find_button_ai(screenshot_path, 'text_input')
    
    def _find_button_ai(self, screenshot_path: str, button_type: str) -> Optional[Tuple[int, int]]:
        """Find button coordinates using AI vision"""
        try:
            if not self.openai_client:
                logger.warning("OpenAI client not available, using fallback detection")
                return self._fallback_button_detection(screenshot_path, button_type)
            
            # Encode image to base64
            base64_image = self._encode_image_to_base64(screenshot_path)
            if not base64_image:
                return None
            
            # Create button-specific prompts
            button_prompts = {
                'like': "Find the LIKE button (usually a heart icon, thumbs up, or green button). Return coordinates as 'x,y' or 'NOT_FOUND'.",
                'pass': "Find the PASS button (usually an X icon, thumbs down, or red button). Return coordinates as 'x,y' or 'NOT_FOUND'.",
                'comment': "Find the COMMENT button (usually a chat bubble or comment icon). Return coordinates as 'x,y' or 'NOT_FOUND'.",
                'send': "Find the SEND button (usually says 'Send' or has a send icon). Return coordinates as 'x,y' or 'NOT_FOUND'.",
                'text_input': "Find the text input field (usually a text box or input area). Return coordinates as 'x,y' or 'NOT_FOUND'."
            }
            
            prompt = f"""
            Analyze this mobile app screenshot and {button_prompts.get(button_type, f"find the {button_type} button")}
            
            The coordinates should be the center point of the button/field.
            Only respond with the coordinates in format 'x,y' or 'NOT_FOUND' if not found.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=20
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NOT_FOUND":
                logger.debug(f"AI could not find {button_type} button")
                return None
            
            # Parse coordinates
            try:
                x, y = map(int, result.split(','))
                logger.debug(f"AI found {button_type} button at ({x}, {y})")
                return (x, y)
            except ValueError:
                logger.error(f"Invalid coordinate format from AI: {result}")
                return None
            
        except Exception as e:
            logger.error(f"Error in AI button detection for {button_type}: {e}")
            return self._fallback_button_detection(screenshot_path, button_type)
    
    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for AI vision API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image to base64: {e}")
            return None
    
    def _fallback_profile_detection(self, screenshot_path: str) -> bool:
        """Fallback profile detection when AI is not available"""
        try:
            # Simple heuristic: check if image exists and has reasonable size
            with Image.open(screenshot_path) as img:
                width, height = img.size
                # Assume profile screens are portrait orientation
                return height > width and height > 1000
        except Exception as e:
            logger.error(f"Error in fallback profile detection: {e}")
            return False
    
    def _fallback_button_detection(self, screenshot_path: str, button_type: str) -> Optional[Tuple[int, int]]:
        """Fallback button detection when AI is not available"""
        try:
            with Image.open(screenshot_path) as img:
                width, height = img.size
                
                # Simple heuristic positioning based on common UI patterns
                if button_type == 'like':
                    # Like button usually bottom right
                    return (int(width * 0.8), int(height * 0.9))
                elif button_type == 'pass':
                    # Pass button usually bottom left
                    return (int(width * 0.2), int(height * 0.9))
                elif button_type == 'comment':
                    # Comment button usually center bottom
                    return (int(width * 0.5), int(height * 0.9))
                elif button_type == 'send':
                    # Send button usually bottom right
                    return (int(width * 0.8), int(height * 0.9))
                elif button_type == 'text_input':
                    # Text input usually center bottom
                    return (int(width * 0.5), int(height * 0.85))
                
                return None
        except Exception as e:
            logger.error(f"Error in fallback button detection: {e}")
            return None
    
    def find_profile_text_region(self, screenshot_path: str) -> Optional[Tuple[int, int, int, int]]:
        """Find the region containing profile text using AI vision"""
        try:
            if not self.openai_client:
                # Fallback to simple heuristic
                with Image.open(screenshot_path) as img:
                    width, height = img.size
                    return (0, height // 2, width, height // 2)
            
            # Encode image to base64
            base64_image = self._encode_image_to_base64(screenshot_path)
            if not base64_image:
                return None
            
            prompt = """
            Analyze this mobile app screenshot and find the region containing profile text/bio information.
            Look for text areas that contain:
            - Name and age
            - Bio/description text
            - Profile prompts and answers
            
            Return the coordinates as 'x,y,width,height' representing the bounding box of the text region.
            If no text region is found, return 'NOT_FOUND'.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=30
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NOT_FOUND":
                logger.debug("AI could not find profile text region")
                return None
            
            # Parse coordinates
            try:
                x, y, w, h = map(int, result.split(','))
                logger.debug(f"AI found profile text region at ({x}, {y}) with size {w}x{h}")
                return (x, y, w, h)
            except ValueError:
                logger.error(f"Invalid coordinate format from AI: {result}")
                return None
            
        except Exception as e:
            logger.error(f"Error finding profile text region: {e}")
            # Fallback to simple heuristic
            try:
                with Image.open(screenshot_path) as img:
                    width, height = img.size
                    return (0, height // 2, width, height // 2)
            except:
                return None
