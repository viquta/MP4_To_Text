import moviepy.editor as mp #remember to install moviepy.editor that is vers 1.0.3 and not latest because of a bug
import speech_recognition as sr
from pydub import AudioSegment
import os
from tqdm import tqdm

def mp4_to_wav(video_path, wav_output_path):
    print("Step 1/3: Converting MP4 to WAV...")
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(wav_output_path)
    print(f"Converted {video_path} to {wav_output_path}\n")

def split_wav(wav_path, segment_length=5*60*1000):
    print("Step 2/3: Checking WAV file length and splitting if necessary...")
    audio = AudioSegment.from_wav(wav_path)
    wav_files = []
    
    if len(audio) > 10*60*1000:  # If longer than 10 minutes
        num_segments = len(audio) // segment_length + 1
        print(f"File is longer than 10 minutes, splitting into {num_segments} parts...")
        for i in range(0, len(audio), segment_length):
            part = audio[i:i + segment_length]
            part_filename = f"{wav_path.rsplit('.', 1)[0]}_part{i//segment_length + 1}.wav"
            part.export(part_filename, format="wav")
            wav_files.append(part_filename)
            print(f"Exported {part_filename} ({(i//segment_length + 1)}/{num_segments})")
    else:
        wav_files.append(wav_path)  # No need to split if under 10 minutes
        print(f"File is under 10 minutes, no need to split.\n")
    
    return wav_files

def wav_to_text(wav_files, output_file):
    print("Step 3/3: Converting WAV files to text...")
    r = sr.Recognizer()
    full_text = ""
    
    for index, wav_file in enumerate(wav_files):
        print(f"\nProcessing file {index + 1}/{len(wav_files)}: {wav_file}")
        audio = AudioSegment.from_wav(wav_file)
        audio_duration = len(audio)  # duration in milliseconds
        progress_bar = tqdm(total=audio_duration, desc=f"Transcribing {wav_file}", unit="ms")
        chunk_length = 10000  # 10 seconds in ms
        for chunk_start in range(0, audio_duration, chunk_length):
            chunk = audio[chunk_start:chunk_start + chunk_length]
            chunk_filename = f"{wav_file}_chunk.wav"
            chunk.export(chunk_filename, format="wav")
            with sr.AudioFile(chunk_filename) as source:
                audio_data = r.record(source)
                try:
                    # recognize_google is a valid method of speech_recognition.Recognizer
                    text = r.recognize_google(audio_data)  # type: ignore
                    full_text += text + " "
                except sr.RequestError as e:
                    print(f"Failed API request: {e}")
                except sr.UnknownValueError:
                    print(f"{wav_file} : Detected unrecognizable speech")
            os.remove(chunk_filename)
            progress_bar.update(chunk_length)
        progress_bar.close()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"Transcription completed. Output saved to {output_file}\n")

    # Delete the split WAV files
    for wav_file in wav_files:
        if "_part" in wav_file:  # Ensure that we are only deleting the split parts
            try:
                os.remove(wav_file)
                print(f"Deleted {wav_file}")
            except OSError as e:
                print(f"Error deleting {wav_file}: {e}")
# Usage
video_path = "/put your mp4 file path here.mp4"
wav_output_path = "/put your wav output file path here.wav"
text_output_path = "/put your text output file path here.txt"

# Step 1: Convert MP4 to WAV
mp4_to_wav(video_path, wav_output_path)

# Step 2: Split WAV file if necessary
wav_files = split_wav(wav_output_path)

# Step 3 & 4: Convert split WAV files to text and save to a single text file
wav_to_text(wav_files, text_output_path)
