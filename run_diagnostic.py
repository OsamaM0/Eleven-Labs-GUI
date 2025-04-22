#!/usr/bin/env python3
import os
import sys
from elevenlabs.client import ElevenLabs
from io import BytesIO
import requests
import tempfile

def run_diagnostic():
    """Run a diagnostic check on the ElevenLabs API integration"""
    print("=== ElevenLabs Voice Changer Diagnostic Tool ===\n")
    
    # 1. Check API key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    
    if not api_key:
        print("❌ API key not found in .env file")
        print("Create a .env file with your API key like this:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API key found (first few chars: {api_key[:5]}...)")
    
    # 2. Initialize client
    try:
        client = ElevenLabs(api_key=api_key)
        print("✅ ElevenLabs client initialized")
    except Exception as e:
        print(f"❌ Error initializing client: {str(e)}")
        return False
    
    # 3. Verify account access
    try:
        user_data = client.user.get()
        print(f"✅ Account verified: {user_data.subscription.tier}")
        print(f"   Characters remaining: {user_data.subscription.character_count}")
        if hasattr(user_data.subscription, "voice_conversion_remaining"):
            print(f"   Voice conversions remaining: {user_data.subscription.voice_conversion_remaining}")
        else:
            print("⚠️ Your subscription tier might not include voice conversion")
    except Exception as e:
        print(f"❌ Error verifying account: {str(e)}")
    
    # 4. Test voice listing
    try:
        voices = client.voices.get_all()
        print(f"✅ Retrieved {len(voices)} voices")
        if len(voices) > 0:
            print(f"   First voice: {voices[0].name} ({voices[0].voice_id})")
    except Exception as e:
        print(f"❌ Error listing voices: {str(e)}")
    
    # 5. Test speech-to-speech conversion with sample audio
    print("\nTesting speech-to-speech conversion...")
    try:
        # Get a small sample audio
        audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
        response = requests.get(audio_url)
        if response.status_code != 200:
            print(f"❌ Could not download sample audio: HTTP {response.status_code}")
            return False
            
        audio_data = BytesIO(response.content)
        print("✅ Sample audio downloaded")
        
        # Try conversion
        voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Default ElevenLabs voice
        print(f"Converting with voice ID: {voice_id}")
        
        try:
            # Get the generator from the API
            output_generator = client.speech_to_speech.convert(
                voice_id=voice_id,
                audio=audio_data,
                model_id="eleven_multilingual_sts_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert generator to bytes
            print("Collecting audio chunks from generator...")
            output_bytes = b''
            chunk_count = 0
            for chunk in output_generator:
                output_bytes += chunk
                chunk_count += 1
                print(f"  Received chunk {chunk_count} ({len(chunk)} bytes)")
            
            print(f"Total audio size: {len(output_bytes)} bytes from {chunk_count} chunks")
            
            # Save it to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(output_bytes)
                output_path = f.name
            
            print(f"✅ Conversion successful! Output saved to: {output_path}")
            print(f"   Try playing this file to verify the voice was changed.")
            return True
        except Exception as e:
            print(f"❌ Speech-to-speech conversion failed: {str(e)}")
            if "subscription" in str(e).lower():
                print("   Your subscription may not include the speech-to-speech feature.")
                print("   This is a premium feature that requires a paid plan.")
            return False
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    if run_diagnostic():
        print("\nAll diagnostics passed! Your setup should be able to use the Voice Changer.")
    else:
        print("\nDiagnostic failed. Please fix the issues above.")
