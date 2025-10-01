"""
Profile Analyzer - AI-powered profile analysis and matching
"""

import openai
import logging
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProfileDecision:
    """Represents a decision about a profile"""
    action: str  # 'like', 'pass', 'comment'
    confidence: float  # 0.0 to 1.0
    reason: str
    comment: Optional[str] = None


class ProfileAnalyzer:
    """Analyzes profiles using AI to make matching decisions"""
    
    def __init__(self, config):
        self.config = config
        self.openai_client = None
        self._setup_openai()
        
        # Default matching criteria
        self.criteria = self.config.get('matching_criteria', {
            'min_age': 21,
            'max_age': 35,
            'preferred_interests': ['technology', 'travel', 'fitness', 'music', 'art'],
            'deal_breakers': ['smoking', 'drugs', 'excessive drinking'],
            'personality_traits': ['intelligent', 'funny', 'adventurous', 'kind']
        })
    
    def _setup_openai(self) -> None:
        """Setup OpenAI client"""
        try:
            api_key = self.config.get('openai_api_key')
            if not api_key:
                logger.error("OpenAI API key not found in configuration")
                return
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
    
    def analyze_profile(self, profile_text: str, screenshot_path: str = None) -> ProfileDecision:
        """Analyze profile using both text and image"""
        try:
            if not self.openai_client:
                logger.warning("OpenAI client not available, using fallback analysis")
                return self._fallback_analysis(profile_text)
            
            # Use AI vision if screenshot is available
            if screenshot_path:
                return self._analyze_profile_with_vision(profile_text, screenshot_path)
            else:
                return self._analyze_profile_text_only(profile_text)
            
        except Exception as e:
            logger.error(f"Error analyzing profile: {e}")
            return self._fallback_analysis(profile_text)
    
    def _analyze_profile_with_vision(self, profile_text: str, screenshot_path: str) -> ProfileDecision:
        """Analyze profile using AI vision"""
        try:
            import base64
            
            # Encode image to base64
            with open(screenshot_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create analysis prompt
            criteria_text = json.dumps(self.criteria, indent=2)
            
            prompt = f"""
            Analyze this dating app profile screenshot and make a matching decision based on the criteria below.

            PROFILE TEXT (if any):
            {profile_text}

            MATCHING CRITERIA:
            {criteria_text}

            Look at both the visual elements (photos, layout) and any text content to make your decision.
            
            Please respond with a JSON object containing:
            1. "action": "like", "pass", or "comment"
            2. "confidence": float between 0.0 and 1.0
            3. "reason": brief explanation of the decision
            4. "comment": if action is "comment", provide a personalized, witty one-liner

            Guidelines:
            - Like profiles that match most criteria and seem compatible
            - Pass on profiles with deal-breakers or poor compatibility
            - Comment on profiles that are interesting but need a conversation starter
            - Be selective but not overly picky
            - Consider age, interests, and personality traits
            - Avoid generic or inappropriate comments

            Response format:
            {{
                "action": "like|pass|comment",
                "confidence": 0.85,
                "reason": "Profile shows good compatibility with shared interests in technology and travel",
                "comment": "Your travel photos look amazing! What's the most adventurous place you've been?"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an AI assistant that analyzes dating profiles and makes matching decisions based on compatibility criteria."
                    },
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
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            decision = self._parse_ai_response(analysis_text)
            
            logger.info(f"Profile analysis (vision): {decision.action} (confidence: {decision.confidence:.2f})")
            return decision
            
        except Exception as e:
            logger.error(f"Error in vision-based profile analysis: {e}")
            return self._analyze_profile_text_only(profile_text)
    
    def _analyze_profile_text_only(self, profile_text: str) -> ProfileDecision:
        """Analyze profile using text only"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(profile_text)
            
            # Get AI analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that analyzes dating profiles and makes matching decisions based on compatibility criteria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            decision = self._parse_ai_response(analysis_text)
            
            logger.info(f"Profile analysis (text): {decision.action} (confidence: {decision.confidence:.2f})")
            return decision
            
        except Exception as e:
            logger.error(f"Error in text-based profile analysis: {e}")
            return self._fallback_analysis(profile_text)
    
    def _create_analysis_prompt(self, profile_text: str) -> str:
        """Create prompt for AI analysis"""
        criteria_text = json.dumps(self.criteria, indent=2)
        
        prompt = f"""
Analyze this dating profile and make a matching decision based on the criteria below.

PROFILE TEXT:
{profile_text}

MATCHING CRITERIA:
{criteria_text}

Please respond with a JSON object containing:
1. "action": "like", "pass", or "comment"
2. "confidence": float between 0.0 and 1.0
3. "reason": brief explanation of the decision
4. "comment": if action is "comment", provide a personalized, witty one-liner

Guidelines:
- Like profiles that match most criteria and seem compatible
- Pass on profiles with deal-breakers or poor compatibility
- Comment on profiles that are interesting but need a conversation starter
- Be selective but not overly picky
- Consider age, interests, and personality traits
- Avoid generic or inappropriate comments

Response format:
{{
    "action": "like|pass|comment",
    "confidence": 0.85,
    "reason": "Profile shows good compatibility with shared interests in technology and travel",
    "comment": "Your travel photos look amazing! What's the most adventurous place you've been?"
}}
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> ProfileDecision:
        """Parse AI response into ProfileDecision object"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                return ProfileDecision(
                    action=data.get('action', 'pass'),
                    confidence=float(data.get('confidence', 0.5)),
                    reason=data.get('reason', 'No reason provided'),
                    comment=data.get('comment')
                )
            else:
                # Fallback parsing
                return self._parse_fallback_response(response_text)
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return self._parse_fallback_response(response_text)
    
    def _parse_fallback_response(self, response_text: str) -> ProfileDecision:
        """Fallback parsing for non-JSON responses"""
        response_lower = response_text.lower()
        
        if 'like' in response_lower:
            action = 'like'
        elif 'comment' in response_lower:
            action = 'comment'
        else:
            action = 'pass'
        
        return ProfileDecision(
            action=action,
            confidence=0.6,
            reason="AI analysis completed",
            comment="Hey! Your profile caught my attention 😊" if action == 'comment' else None
        )
    
    def _fallback_analysis(self, profile_text: str) -> ProfileDecision:
        """Fallback analysis when AI is not available"""
        try:
            # Simple keyword-based analysis
            text_lower = profile_text.lower()
            
            # Check for deal breakers
            deal_breakers = self.criteria.get('deal_breakers', [])
            for breaker in deal_breakers:
                if breaker.lower() in text_lower:
                    return ProfileDecision(
                        action='pass',
                        confidence=0.9,
                        reason=f"Deal breaker found: {breaker}"
                    )
            
            # Check for preferred interests
            interests = self.criteria.get('preferred_interests', [])
            interest_matches = sum(1 for interest in interests if interest.lower() in text_lower)
            
            # Check for age (simple heuristic)
            age_match = self._check_age_match(profile_text)
            
            # Make decision based on matches
            if interest_matches >= 2 and age_match:
                return ProfileDecision(
                    action='like',
                    confidence=0.7,
                    reason=f"Good match: {interest_matches} shared interests"
                )
            elif interest_matches >= 1:
                return ProfileDecision(
                    action='comment',
                    confidence=0.6,
                    reason="Some shared interests, worth a conversation",
                    comment="Hey! I noticed we have some things in common 😊"
                )
            else:
                return ProfileDecision(
                    action='pass',
                    confidence=0.5,
                    reason="Limited compatibility"
                )
                
        except Exception as e:
            logger.error(f"Error in fallback analysis: {e}")
            return ProfileDecision(
                action='pass',
                confidence=0.3,
                reason="Analysis failed"
            )
    
    def _check_age_match(self, profile_text: str) -> bool:
        """Check if age matches criteria"""
        try:
            import re
            
            # Extract age from text
            age_pattern = r'\b(\d{2})\b'
            ages = re.findall(age_pattern, profile_text)
            
            if not ages:
                return True  # Assume match if no age found
            
            # Check if any age is in range
            min_age = self.criteria.get('min_age', 21)
            max_age = self.criteria.get('max_age', 35)
            
            for age_str in ages:
                age = int(age_str)
                if min_age <= age <= max_age:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking age: {e}")
            return True  # Assume match on error
    
    def generate_comment(self, profile_text: str) -> str:
        """Generate a personalized comment for a profile"""
        try:
            if not self.openai_client:
                return "Hey! Your profile caught my attention 😊"
            
            prompt = f"""
Generate a personalized, witty one-liner comment for this dating profile. 
Keep it light, fun, and engaging. Avoid being generic or inappropriate.

PROFILE TEXT:
{profile_text}

Guidelines:
- Be specific to something mentioned in their profile
- Keep it under 50 characters
- Make it conversation-starting
- Be respectful and genuine
- Use emojis sparingly

Generate just the comment, no explanation needed.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a witty, charming person writing dating app comments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=50
            )
            
            comment = response.choices[0].message.content.strip()
            return comment
            
        except Exception as e:
            logger.error(f"Error generating comment: {e}")
            return "Hey! Your profile caught my attention 😊"
    
    def update_criteria(self, new_criteria: Dict) -> None:
        """Update matching criteria"""
        self.criteria.update(new_criteria)
        logger.info("Matching criteria updated")
    
    def get_criteria(self) -> Dict:
        """Get current matching criteria"""
        return self.criteria.copy()
