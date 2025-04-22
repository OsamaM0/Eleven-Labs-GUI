import os
import sys
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import requests
from io import BytesIO

# Load environment variables first
load_dotenv()

# Check API key
from config import ELEVEN_LABS_API_KEY
api_key = ELEVEN_LABS_API_KEY

print(f"API Key present: {'Yes' if api_key else 'No'}")
print(f"API Key format: {'Valid format (not showing full key)' if len(api_key) > 30 else 'Possibly invalid format'}")

# Initialize the client
try:
    client = ElevenLabs(api_key=api_key)
    print("ElevenLabs client initialized successfully")
except Exception as e:
    print(f"Error initializing ElevenLabs client: {e}")
    sys.exit(1)

# Check if we can fetch voices
try:
    print("\nTesting voice listing...")
    voices = client.voices.get_all()
    print(f"Successfully retrieved {len(voices)} voices")
    print("First few voices:")
    for i, voice in enumerate(voices[:3]):  # Show first 3 voices
        print(f"  {i+1}. {voice.name} (ID: {voice.voice_id})")
except Exception as e:
    print(f"Error fetching voices: {e}")

# Test the speech-to-speech functionality
test_voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Default voice ID
print("\nTesting speech-to-speech conversion...")

try:
    # Download a test audio file
    print("Downloading test audio file...")
    audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
    response = requests.get(audio_url)
    
    if response.status_code != 200:
        print(f"Error downloading test audio: HTTP {response.status_code}")
    else:
        print("Test audio downloaded successfully")
        audio_data = BytesIO(response.content)
        
        # Try the conversion
        print("Attempting voice conversion...")
        try:
            audio_stream = client.speech_to_speech.convert(
                voice_id=test_voice_id,
                audio=audio_data,
                model_id="eleven_multilingual_sts_v2",
                output_format="mp3_44100_128",
            )
            
            # Save the result to test playback
            with open("test_output.mp3", "wb") as f:
                f.write(audio_stream)
            print("Voice conversion successful! Output saved to test_output.mp3")
            
        except Exception as e:
            print(f"Speech-to-speech conversion failed: {e}")
except Exception as e:
    print(f"General error during testing: {e}")
