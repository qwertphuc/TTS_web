import asyncio
import os
import time
import threading
from edge_tts import Communicate

# Define valid voices
VALID_VOICES = ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]

# Directory configuration (matching app.py)
MEDIA_FOLDER = 'media'
SHORT_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'short')
LONG_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'long')
TRASH_FOLDER = os.path.join(MEDIA_FOLDER, 'trash')

# Ensure directories exist
os.makedirs(SHORT_MEDIA_FOLDER, exist_ok=True)
os.makedirs(LONG_MEDIA_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

# Async TTS function
async def text_to_speech(text, voice, output_file):
    """Generate audio from text using the TTS model."""
    if voice not in VALID_VOICES:
        voice = "vi-VN-HoaiMyNeural"  # Default voice
    tts = Communicate(text, voice)
    await tts.save(output_file)

# Sync wrapper for TTS
def run_tts(input_text, voice, save_path):
    """Run the TTS process synchronously."""
    asyncio.run(text_to_speech(input_text, voice, save_path))

# Function to split text into chunks
def split_text_into_chunks(text, max_chunk_size=200):
    """Split text into chunks of approximately max_chunk_size, ensuring chunks end at the nearest sentence boundary (., \n)."""
    chunks = []
    start = 0

    while start < len(text):
        # Determine the end position for the chunk
        end = start + max_chunk_size

        # If the end is beyond the text length, set it to the end of the text
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Find the nearest sentence boundary (., \n) before the end
        boundary = max(text.rfind(".", start, end), text.rfind("\n", start, end))

        # If no boundary is found, just split at the end
        if boundary == -1:
            boundary = end

        # Append the chunk
        chunks.append(text[start:boundary + 1].strip())

        # Move the start to the next character after the boundary
        start = boundary + 1

    return chunks

# Function to process text with enable_flow
def process_text_with_flow(text, voice, storage_folder):
    """Process text with enable_flow enabled."""
    timestamp = int(time.time())
    final_audio_filename = f"audio_{timestamp}.mp3"
    final_audio_path = os.path.join(storage_folder, final_audio_filename)

    # Split text into chunks and process in parallel
    chunks = split_text_into_chunks(text)
    chunked_audio_files = []

    # Process each chunk in a separate thread
    threads = []
    for i, chunk in enumerate(chunks):
        chunk_filename = f"chunk_{timestamp}_{i}.mp3"
        chunk_path = os.path.join(TRASH_FOLDER, chunk_filename)
        thread = threading.Thread(target=run_tts, args=(chunk, voice, chunk_path))
        thread.start()
        threads.append(thread)
        chunked_audio_files.append(chunk_path)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Combine chunked audio files into a single file
    from pydub import AudioSegment  # Import here to avoid dependency issues
    combined_audio = AudioSegment.empty()
    for chunk_file in chunked_audio_files:
        combined_audio += AudioSegment.from_file(chunk_file)
    combined_audio.export(final_audio_path, format="mp3")

    # Delete chunked audio files after combining
    for chunk_file in chunked_audio_files:
        os.remove(chunk_file)

    return final_audio_filename, final_audio_path

# Function to process text without enable_flow
def process_text_without_flow(text, voice, storage_folder):
    """Process text with enable_flow disabled."""
    timestamp = int(time.time())
    final_audio_filename = f"audio_{timestamp}.mp3"
    final_audio_path = os.path.join(storage_folder, final_audio_filename)

    # Process the entire text as a single audio file
    run_tts(text, voice, final_audio_path)

    return final_audio_filename, final_audio_path