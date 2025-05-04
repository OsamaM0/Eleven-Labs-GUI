#!/usr/bin/env python3
import os
import sys
from voice_changer import VoiceChanger
from io import BytesIO
import requests
import tempfile

def run_diagnostic():
    """Run a diagnostic check on the ElevenLabs API integration using VoiceChanger"""
    print("=== ElevenLabs Voice Changer Diagnostic Tool ===\n")
    
    # 1. Check API key
    from dotenv import load_dotenv
    load_dotenv()
    from config import ELEVEN_LABS_API_KEY
    api_key = ELEVEN_LABS_API_KEY
    
    if not api_key:
        print("❌ API key not found in .env file or config.py")
        print("Create a .env file with your API key like this:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API key found (first few chars: {api_key[:5]}...)")
    
    # 2. Initialize VoiceChanger
    try:
        voice_changer = VoiceChanger()
        print("✅ VoiceChanger initialized")
    except Exception as e:
        print(f"❌ Error initializing VoiceChanger: {str(e)}")
        return False
    
    # 3. Verify account access
    try:
        success, message = voice_changer.validate_connection()
        if success:
            print(f"✅ {message}")
        else:
            print(f"⚠️ {message}")
    except Exception as e:
        print(f"❌ Error verifying account: {str(e)}")
    
    # 4. Test voice listing
    try:
        voices = voice_changer.get_available_voices()
        print(f"✅ Retrieved {len(voices)} voices")
        if len(voices) > 0:
            first_voice = list(voices.keys())[0]
            print(f"   First voice: {first_voice} ({voices[first_voice]['id']})")
    except Exception as e:
        print(f"❌ Error listing voices: {str(e)}")
    
    # 5. Test speech-to-speech conversion with sample audio
    print("\nTesting speech-to-speech conversion...")
    try:
        # Get a small sample audio
        audio_url = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
        
        # Test the voice conversion using the VoiceChanger class
        voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Default ElevenLabs voice
        print(f"Converting with voice ID: {voice_id}")
        
        success, result = voice_changer.change_voice(
            input_audio_url=audio_url,
            voice_id=voice_id
        )
        
        if success:
            print(f"✅ Conversion successful! Output saved to: {result}")
            print(f"   Try playing this file to verify the voice was changed.")
            return True
        else:
            print(f"❌ Voice conversion failed: {result}")
            if "subscription" in result.lower():
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
