import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import requests
from io import BytesIO
import tempfile
import math
from config import ELEVEN_LABS_API_KEY, ELEVEN_LABS_API_URL, DEFAULT_VOICE_PRICE_PER_MIN

class VoiceChanger:
    def __init__(self):
        self.api_key = ELEVEN_LABS_API_KEY
        self.api_url = ELEVEN_LABS_API_URL
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables or config")
        self.client = ElevenLabs(api_key=self.api_key)
        
    def validate_connection(self):
        """Validate the API connection and key"""
        try:
            # Check user subscription first
            user_data = self.client.user.get()
            subscription = user_data.subscription
            
            # Check if speech-to-speech is available on this subscription
            has_sts = hasattr(subscription, "voice_conversion_remaining") and subscription.voice_conversion_remaining > 0
            
            if not has_sts:
                return False, "Your subscription does not include voice changing capabilities or you have no conversions remaining"
                
            voices = self.client.voices.get_all()
            return True, f"Connection successful. You have {subscription.voice_conversion_remaining} voice conversions remaining."
        except Exception as e:
            return False, f"API connection error: {str(e)}"
    
    def get_available_voices(self):
        """Get comprehensive list of available voices with detailed metadata"""
        try:
            voices = self.client.voices.search(page_size=100, sort="name")
            
            voice_options = {}
            for voice in voices.dict().get("voices", []):
                voice_options[voice["name"]] = {
                    "id": voice.get("voice_id", ""),
                    "preview_url": voice.get("preview_url", ""),
                    "accent": voice.get("labels", {}).get("accent", ""),
                    "description": voice.get("labels", {}).get("description", ""),
                    "age": voice.get("labels", {}).get("age", ""),
                    "gender": voice.get("labels", {}).get("gender", ""),
                    "use_case": voice.get("labels", {}).get("use_case", ""),
                    "price_per_min": self.get_voice_price(getattr(voice, "category", "premium"))
                }
            return voice_options
        except Exception as e:
            print(f"Error fetching voices: {e}")
            # Return default voices
            return {
                "Rachel": {"id": "21m00Tcm4TlvDq8ikWAM", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30},
                "Domi": {"id": "AZnzlk1XvdvUeBnXmlld", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30},
                "Bella": {"id": "EXAVITQu4vr4xnSDxMaL", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30},
                "Antoni": {"id": "MF3mGyEYCl7XYWbV9V6O", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30},
                "Josh": {"id": "TxGEqnHWrfWFTfGW9XjX", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30},
                "Nicole": {"id": "JBFqnCBsd6RMkjVDRZzb", "preview_url": "", "accent": "", "description": "", "age": "", "gender": "", "use_case": "", "price_per_min": 0.30}
            }
    
    def get_voice_price(self, category="premium"):
        """Get price per minute based on voice category"""
        # These prices should be updated based on current Eleven Labs pricing
        prices = {
            "premium": 0.20,
            "standard": 0.2,
            "professional": 0.2
        }
        return prices.get(category.lower(), 0.20)

    def calculate_cost(self, duration_minutes, price_per_min=None):
        """Calculate cost for voice conversion based on duration"""
        # Use the price from config if none is provided
        if price_per_min is None:
            price_per_min = DEFAULT_VOICE_PRICE_PER_MIN
        return round(duration_minutes * price_per_min, 2)
    
    def change_voice(self, input_audio_path=None, input_audio_url=None, voice_id="JBFqnCBsd6RMkjVDRZzb", model_id="eleven_multilingual_sts_v2"):
        """
        Change the voice in an audio file
        
        Args:
            input_audio_path: Path to local audio file
            input_audio_url: URL to audio file
            voice_id: Target voice ID
            model_id: Model to use for conversion
            
        Returns:
            (success, result) where:
                success: Boolean indicating success
                result: If success, path to output audio file; otherwise error message
        """
        try:
            # Get audio data
            audio_data = None
            if input_audio_path and os.path.exists(input_audio_path):
                # For local files, read them as binary and create a BytesIO object
                with open(input_audio_path, 'rb') as f:
                    file_data = f.read()
                    audio_data = BytesIO(file_data)
                    audio_data.name = os.path.basename(input_audio_path)  # Add name attribute
            elif input_audio_url:
                response = requests.get(input_audio_url)
                if response.status_code == 200:
                    audio_data = BytesIO(response.content)
                    audio_data.name = "audio_from_url.mp3"  # Add name attribute
                else:
                    return False, f"Failed to download audio: HTTP {response.status_code}"
            else:
                return False, "No input audio provided"
            
            # Convert audio using speech-to-speech API
            try:
                # Get the generator from the API
                audio_stream_generator = self.client.speech_to_speech.convert(
                    voice_id="IES4nrmZdUBHByLBde0P",
                    audio=audio_data,
                    model_id=model_id,
                    output_format="mp3_44100_128",
                )
                
                # Convert generator to bytes by concatenating all chunks
                audio_bytes = b''
                for chunk in audio_stream_generator:
                    audio_bytes += chunk
                
                # Save the audio to a temporary file that can be played by the GUI
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
                temp_file.close()
                
                return True, temp_file_path
            except Exception as api_error:
                if "Server disconnected" in str(api_error):
                    return False, "Server disconnected without sending a response. Please try again later."
                if "Subscription missing" in str(api_error) or "upgrade your plan" in str(api_error).lower():
                    return False, "Your subscription does not include voice changing capabilities. Please upgrade your ElevenLabs plan."
                return False, f"API error: {str(api_error)}"
            
        except Exception as e:
            return False, f"Error during voice conversion: {str(e)}"
