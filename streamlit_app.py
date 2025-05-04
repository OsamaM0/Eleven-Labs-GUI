import streamlit as st
import tempfile
import os
import time
from controllers import voice_changer_controller
from voice_changer import VoiceChanger
from models.media_processor import is_video_file, extract_audio_from_video
from config import MAX_SEGMENT_DURATION_MS  # Import configuration values

st.title("Eleven Labs Voice Changer")
st.markdown("### Upload your audio or video file")

# Initialize voice changer
voice_changer = VoiceChanger()

# Update file uploader to accept more formats
uploaded_file = st.file_uploader("Choose an audio or video file", 
                                type=["wav", "mp3", "mp4", "avi", "mov", "mkv", "flv", "wmv"])

# Get voice options from Eleven Labs API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_voices():
    with st.spinner("Loading available voices..."):
        return voice_changer.get_available_voices()

voice_options = get_voices()
selected_voice_name = st.selectbox("Select Voice", [f"{voice} ({voice_options[voice]['accent']} - {voice_options[voice]['description']} - {voice_options[voice]['age']} - {voice_options[voice]['gender']} - {voice_options[voice]['use_case']})" for voice in voice_options.keys()])
selected_voice = voice_options[selected_voice_name.split("(")[0].strip()]

# Show voice preview if available
if selected_voice.get("preview_url"):
    st.audio(selected_voice["preview_url"])

st.markdown("### Processed Media Preview")

if uploaded_file:
    # Save uploaded file to temporary file
    temp_dir = tempfile.TemporaryDirectory()
    input_path = os.path.join(temp_dir.name, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Check if it's a video file
    is_video = is_video_file(input_path)
    # Display the uploaded file
    if is_video:
        st.video(input_path)
        # Extract audio for duration calculation
        audio_path = extract_audio_from_video(input_path)
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)  # Clean up
    else:
        st.audio(input_path)
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
    
    # Calculate cost preview using configuration
    duration_minutes = len(audio) / 60000
    # Use the calculate_cost method from VoiceChanger which should use config values
    estimated_cost = voice_changer.calculate_cost(duration_minutes, selected_voice.get("price_per_min", None))
    
    # Display processing information
    st.markdown(f"### Audio Information:")
    st.markdown(f"- Duration: {duration_minutes:.2f} minutes")
    st.markdown(f"- Estimated Cost: ${estimated_cost}")
    
    # Calculate number of chunks based on config value, not hardcoded 240000
    num_chunks = (len(audio) + MAX_SEGMENT_DURATION_MS - 1) // MAX_SEGMENT_DURATION_MS
    st.markdown(f"- File will be processed in {num_chunks} chunk(s) of {MAX_SEGMENT_DURATION_MS/60000:.1f} minutes or less")
    
    if st.button("Change Voice"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process the voice change
        status_text.text("Processing audio chunks...")
        
        try:
            with st.spinner("Processing... This may take a while for large files"):
                start_time = time.time()
                output_path, total_cost = voice_changer_controller.process_voice_change(input_path, selected_voice)
                processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            status_text.text(f"Processing complete! Time taken: {processing_time:.2f} seconds")
            
            st.success(f"Voice changed! Total cost: ${total_cost}")
            
            # Display the processed file
            if is_video_file(output_path):
                st.video(output_path)
            else:
                st.audio(output_path)
                
            # Provide download option
            with open(output_path, "rb") as f:
                st.download_button("Download Changed Media", f, file_name=os.path.basename(output_path))
        except Exception as e:
            progress_bar.progress(100)
            st.error(f"Error during voice changing: {str(e)}")
            status_text.text("Processing failed. Please check your API key and try again.")
