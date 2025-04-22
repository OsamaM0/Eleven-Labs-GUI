import requests
import os
import time
from pydub import AudioSegment
import streamlit as st
from elevenlabs.client import ElevenLabs
from io import BytesIO
import tempfile

# Get API key from config
from config import ELEVEN_LABS_API_KEY, ELEVEN_LABS_API_URL

# Use config values instead of hardcoded values
API_KEY = ELEVEN_LABS_API_KEY
API_URL = ELEVEN_LABS_API_URL

# Initialize the ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=API_KEY)

def get_voice_options():
    """Get available voices from Eleven Labs API"""
    try:
        voices = elevenlabs_client.voices.get_all()
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
                    "price_per_min": get_voice_price(getattr(voice, "category", "premium"))
                }
        return voice_options
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        print(f"Error fetching voices: {e}")
    
    # Fallback to simulated voices if API call fails
    return {
        "Rachel": {
            "id": "21m00Tcm4TlvDq8ikWAM",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        },
        "Domi": {
            "id": "AZnzlk1XvdvUeBnXmlld",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        },
        "Bella": {
            "id": "EXAVITQu4vr4xnSDxMaL",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        },
        "Antoni": {
            "id": "MF3mGyEYCl7XYWbV9V6O",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        },
        "Josh": {
            "id": "TxGEqnHWrfWFTfGW9XjX",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        },
        "Nicole": {
            "id": "JBFqnCBsd6RMkjVDRZzb",
            "preview_url": "",
            "accent": "",
            "description": "",
            "age": "",
            "gender": "",
            "use_case": "",
            "price_per_min": 0.30
        }
    }

def get_voice_price(category="premium"):
    """Get price per minute based on voice category"""
    # These prices should be updated based on current Eleven Labs pricing
    prices = {
        "premium": 0.20,
        "standard": 0.2,
        "professional": 0.2
    }
    return prices.get(category.lower(), 0.20)

def calculate_cost(duration_minutes, price_per_min):
    return round(duration_minutes * price_per_min, 2)

def voice_change_audio_segment(segment_path, voice_id):
    """Change voice of audio segment using Eleven Labs API"""
    try:
        # Load the audio file
        audio = AudioSegment.from_file(segment_path)
        
        # Check if audio is within the 5-minute limit
        if len(audio) > 5 * 60 * 1000:  # 5 minutes in milliseconds
            st.warning(f"Warning: Audio segment exceeds 5 minutes, it may be rejected by API")
            print(f"Warning: Audio segment exceeds 5 minutes, it may be rejected by API")
        
        # Convert the audio to bytes for the SDK
        temp_mp3 = segment_path.replace('.wav', '_temp.mp3')
        audio.export(temp_mp3, format="mp3")
        
        # Prepare the audio data
        with open(temp_mp3, "rb") as f:
            file_data = f.read()
            audio_data = BytesIO(file_data)
            audio_data.name = os.path.basename(temp_mp3)  # Add name attribute
        
        st.info(f"Sending audio to Eleven Labs for voice changing...")
        
        # Use the speech_to_speech method from the SDK
        try:
            # Get the generator from the API
            audio_output_generator = elevenlabs_client.speech_to_speech.convert(
                voice_id=voice_id,
                audio=audio_data,
                model_id="eleven_multilingual_sts_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert generator to bytes by consuming all chunks
            audio_bytes = b''
            for chunk in audio_output_generator:
                audio_bytes += chunk
            
            # Save the audio output
            output_path = segment_path.replace(".wav", f"_changed_{voice_id}.wav")
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
                
            st.success(f"Voice change successful for segment")
            
        except Exception as api_error:
            error_msg = f"Speech-to-Speech API error: {str(api_error)}"
            st.error(error_msg)
            
            if "Subscription missing" in str(api_error) or "upgrade your plan" in str(api_error).lower():
                error_msg = "Your subscription does not include voice changing capabilities. Please upgrade your ElevenLabs plan."
                
            raise Exception(error_msg)
            
        # Clean up temporary file
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
            
        return output_path
            
    except Exception as e:
        error_msg = f"Error during voice change: {str(e)}"
        st.error(error_msg)
        print(error_msg)
        raise Exception(error_msg)
