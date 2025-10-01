"""
Text Extractor - OCR module for extracting text from screenshots
"""

import pytesseract
import logging
from typing import Optional, List, Dict
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extracts text from images using OCR"""
    
    def __init__(self, config):
        self.config = config
        self.tesseract_config = self.config.get('tesseract_config', '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!? ')
        
    def extract_text(self, image_path: str, region: Optional[tuple] = None) -> str:
        """Extract text from image or image region"""
        try:
            # Load image with PIL
            image = Image.open(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return ""
            
            # Crop to region if specified
            if region:
                x, y, w, h = region
                image = image.crop((x, y, x + w, y + h))
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            # Clean up text
            cleaned_text = self._clean_text(text)
            
            logger.debug(f"Extracted text: {cleaned_text[:100]}...")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_profile_info(self, image_path: str) -> Dict[str, str]:
        """Extract structured profile information"""
        try:
            # Load image with PIL
            image = Image.open(image_path)
            if image is None:
                return {}
            
            # Get image dimensions
            width, height = image.size
            
            # Define regions for different profile elements
            regions = {
                'name': (0, 0, width, height // 4),  # Top quarter
                'age': (0, height // 4, width // 3, height // 8),  # Top right
                'bio': (0, height // 2, width, height // 2),  # Bottom half
                'prompts': (0, height // 2, width, height // 2)  # Bottom half
            }
            
            profile_info = {}
            
            for field, region in regions.items():
                text = self.extract_text(image_path, region)
                if text.strip():
                    profile_info[field] = text.strip()
            
            return profile_info
            
        except Exception as e:
            logger.error(f"Error extracting profile info: {e}")
            return {}
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results using PIL"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                gray = image.convert('L')
            else:
                gray = image
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            blurred = enhanced.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Resize image for better OCR (if too small)
            width, height = blurred.size
            if height < 100 or width < 100:
                scale_factor = max(100 / height, 100 / width)
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                blurred = blurred.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return blurred
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Remove common OCR artifacts
            text = text.replace('|', 'I')
            text = text.replace('0', 'O')  # Sometimes numbers are misread
            
            # Remove empty lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text
    
    def extract_text_with_confidence(self, image_path: str) -> List[Dict[str, any]]:
        """Extract text with confidence scores"""
        try:
            # Load image with PIL
            image = Image.open(image_path)
            if image is None:
                return []
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            # Filter out low confidence results
            results = []
            for i in range(len(data['text'])):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if confidence > 30 and text:  # Minimum confidence threshold
                    results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting text with confidence: {e}")
            return []
    
    def is_text_region(self, image_path: str, region: tuple) -> bool:
        """Check if a region contains significant text"""
        try:
            text = self.extract_text(image_path, region)
            # Consider it a text region if it has more than 10 characters
            return len(text.strip()) > 10
            
        except Exception as e:
            logger.error(f"Error checking text region: {e}")
            return False
