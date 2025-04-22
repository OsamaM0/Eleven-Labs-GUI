from pydub import AudioSegment
import os
import tempfile

# Use the correct import structure for MoviePy < 2.0.0
from moviepy.editor import VideoFileClip, AudioFileClip

def is_video_file(file_path):
    """Determine if the file is a video based on extension"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    _, ext = os.path.splitext(file_path.lower())
    return ext in video_extensions

def load_audio(file_path):
    """Load audio file"""
    return AudioSegment.from_file(file_path)

def extract_audio_from_video(video_path):
    """Extract audio from video file"""
    temp_audio_path = video_path + "_extracted_audio.wav"
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(temp_audio_path)
    return temp_audio_path

def segment_media(file_path, segment_duration_ms=4*60*1000):
    """Segment audio or video file into chunks"""
    if is_video_file(file_path):
        # For video, first extract the audio
        audio_path = extract_audio_from_video(file_path)
        return segment_audio(audio_path, segment_duration_ms), True
    else:
        # For audio files
        return segment_audio(file_path, segment_duration_ms), False

def segment_audio(file_path, segment_duration_ms=4*60*1000):
    """Split audio into segments"""
    audio = load_audio(file_path)
    segments = []
    total_length = len(audio)
    for i in range(0, total_length, segment_duration_ms):
        segment = audio[i:i+segment_duration_ms]
        segment_path = file_path.replace(".", f"_segment_{i//segment_duration_ms}.")
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
    return segments

def merge_audio(segments, output_path):
    """Merge audio segments back together"""
    combined = AudioSegment.empty()
    for seg in segments:
        audio_seg = AudioSegment.from_file(seg)
        combined += audio_seg
    combined.export(output_path, format="wav")
    # Clean up temporary segment files
    for seg in segments:
        if os.path.exists(seg):
            os.remove(seg)
    return output_path

def replace_video_audio(video_path, new_audio_path, output_path):
    """Replace the audio in a video with processed audio"""
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(new_audio_path)
    video = video.set_audio(new_audio)
    video.write_videofile(output_path)
    return output_path
