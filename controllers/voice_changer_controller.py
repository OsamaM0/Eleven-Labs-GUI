import os
import math
import streamlit as st
from voice_changer import VoiceChanger
from models.media_processor import segment_media, merge_audio, is_video_file, replace_video_audio
from config import MAX_SEGMENT_DURATION_MS  # Import configuration value

# Initialize the voice changer
voice_changer = VoiceChanger()

def process_voice_change(input_file_path, voice_option):
    # Determine if we're processing video or audio
    is_video = is_video_file(input_file_path)
    
    # Segment the media file
    st.info("Segmenting media...")
    segments, is_extracted_audio = segment_media(input_file_path)
    
    processed_segments = []
    total_segments = len(segments)
    total_cost = 0
    
    st.info(f"Processing {total_segments} segments...")
    for i, seg in enumerate(segments):
        st.write(f"Processing segment {i+1}/{total_segments}")
        success, result = voice_changer.change_voice(
            input_audio_path=seg,
            voice_id=voice_option["id"]
        )
        
        if not success:
            st.error(f"Error processing segment {i+1}: {result}")
            raise Exception(result)
            
        processed_segments.append(result)
    
    # Create the base file path for output
    base_name, ext = os.path.splitext(input_file_path)
    audio_output_path = f"{base_name}_changed_{voice_option['id']}.wav"
    
    # Merge the processed audio segments
    st.info("Merging processed segments...")
    merged_audio = merge_audio(processed_segments, audio_output_path)
    
    # Calculate the cost
    from pydub import AudioSegment
    audio = AudioSegment.from_file(merged_audio)
    duration_ms = len(audio)
    total_minutes = math.ceil(duration_ms / 60000)
    # Use the price from the voice option if available, otherwise None to use default
    total_cost = voice_changer.calculate_cost(total_minutes, voice_option.get("price_per_min", None))
    
    # If we're processing video, replace the audio in the video
    if is_video:
        st.info("Replacing audio in video...")
        video_output_path = f"{base_name}_changed_{voice_option['id']}{ext}"
        final_output = replace_video_audio(input_file_path, merged_audio, video_output_path)
        # Clean up the intermediate audio file
        if os.path.exists(merged_audio) and merged_audio != input_file_path:
            os.remove(merged_audio)
        return final_output, total_cost
    else:
        return merged_audio, total_cost
