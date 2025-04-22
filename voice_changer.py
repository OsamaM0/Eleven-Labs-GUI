import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import requests
from io import BytesIO
import tempfile

class VoiceChanger:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        self.client = ElevenLabs(api_key=api_key)
        
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
        """Get list of available voices"""
        try:
            voices = self.client.voices.get_all()
            result = []
            for v in voices:
                if hasattr(v, "voice_id"):
                    result.append((v.voice_id, v.name))
                elif isinstance(v, (tuple, list)):
                    result.append((v[0], v[1]))
                else:
                    result.append(("", "Unknown"))
            return result
        except Exception as e:
            print(f"Error fetching voices: {e}")
            # Return default voices
            return [
                ("21m00Tcm4TlvDq8ikWAM", "Rachel"),
                ("AZnzlk1XvdvUeBnXmlld", "Domi"),
                ("EXAVITQu4vr4xnSDxMaL", "Bella"),
                ("MF3mGyEYCl7XYWbV9V6O", "Antoni"),
                ("TxGEqnHWrfWFTfGW9XjX", "Josh"),
                ("JBFqnCBsd6RMkjVDRZzb", "Nicole"),
            ]
    
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
                    voice_id=voice_id,
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
