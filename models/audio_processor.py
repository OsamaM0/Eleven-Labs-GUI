from pydub import AudioSegment
import os

def load_audio(file_path):
    return AudioSegment.from_file(file_path)

def segment_audio(file_path, segment_duration_ms=240*1000):
    audio = load_audio(file_path)
    segments = []
    total_length = len(audio)
    for i in range(0, total_length, segment_duration_ms):
        segment = audio[i:i+segment_duration_ms]
        segment_path = file_path.replace(".wav", f"_segment_{i}.wav")
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
    return segments

def merge_audio(segments, output_path):
    combined = AudioSegment.empty()
    for seg in segments:
        audio_seg = AudioSegment.from_file(seg)
        combined += audio_seg
    combined.export(output_path, format="wav")
    # Optionally, remove temporary segments
    for seg in segments:
        os.remove(seg)
    return output_path
