"""
AI-powered caption and title generator
Uses Gemini API first, falls back to OpenAI, then default caption
"""
import google.generativeai as genai
from openai import OpenAI
import os
import tempfile


class AICaptionGenerator:
    def __init__(self, gemini_key=None, openai_key=None, default_caption=""):
        """
        Initialize AI caption generator
        
        Args:
            gemini_key: Google Gemini API key
            openai_key: OpenAI API key
            default_caption: Fallback caption if both AI services fail
        """
        self.gemini_key = gemini_key
        self.openai_key = openai_key
        self.default_caption = default_caption
        
        # Track which API is working
        self.gemini_available = False
        self.openai_available = False
        
        # Initialize Gemini if key provided
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                # Use gemini-2.0-flash (latest stable model)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.gemini_available = True
                print("✓ Gemini AI configured")
            except Exception as e:
                print(f"Note: Gemini initialization failed: {e}")
        
        # Initialize OpenAI if key provided
        if self.openai_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_key)
                self.openai_available = True
                print("✓ OpenAI configured")
            except Exception as e:
                print(f"Note: OpenAI initialization failed: {e}")
    
    def generate_caption_from_filename(self, filename):
        """
        Generate caption and title from video filename
        
        Args:
            filename: Video filename
            
        Returns:
            dict with 'title' and 'caption'
        """
        # Try Gemini first
        if self.gemini_available:
            try:
                result = self._generate_with_gemini(filename)
                if result:
                    print("✓ Generated caption with Gemini AI")
                    return result
            except Exception as e:
                print(f"Gemini generation failed: {e}")
                self.gemini_available = False
        
        # Fallback to OpenAI
        if self.openai_available:
            try:
                result = self._generate_with_openai(filename)
                if result:
                    print("✓ Generated caption with OpenAI")
                    return result
            except Exception as e:
                print(f"OpenAI generation failed: {e}")
                self.openai_available = False
        
        # Use default
        print("Using default caption")
        return {
            'title': filename[:50],
            'caption': self.default_caption
        }
    
    def _generate_with_gemini(self, filename):
        """Generate using Gemini AI"""
        prompt = f"""
Based on this video filename: "{filename}"

Generate:
1. A catchy Instagram title (max 50 characters)
2. An engaging Instagram caption (2-3 sentences) with relevant hashtags

Format your response as:
TITLE: [title here]
CAPTION: [caption here]
"""
        
        response = self.gemini_model.generate_content(prompt)
        return self._parse_ai_response(response.text)
    
    def _generate_with_openai(self, filename):
        """Generate using OpenAI"""
        prompt = f"""
Based on this video filename: "{filename}"

Generate:
1. A catchy Instagram title (max 50 characters)
2. An engaging Instagram caption (2-3 sentences) with relevant hashtags

Format your response as:
TITLE: [title here]
CAPTION: [caption here]
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Instagram content expert who creates engaging titles and captions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return self._parse_ai_response(response.choices[0].message.content)
    
    def _parse_ai_response(self, text):
        """Parse AI response to extract title and caption"""
        try:
            lines = text.strip().split('\n')
            title = ""
            caption = ""
            
            for line in lines:
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                elif line.startswith('CAPTION:'):
                    caption = line.replace('CAPTION:', '').strip()
            
            # If parsing failed, use the whole text as caption
            if not title and not caption:
                caption = text.strip()
                title = filename[:50]
            
            return {
                'title': title or "Amazing Video",
                'caption': caption or self.default_caption
            }
        except:
            return None
