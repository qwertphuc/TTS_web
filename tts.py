import asyncio
import os
import time
import threading
from edge_tts import Communicate
from googletrans import Translator, LANGUAGES

# Define valid voices with language support
VALID_VOICES = {
    "vi": ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"],  # Tiếng Việt
    "en": ["en-US-JennyNeural", "en-GB-RyanNeural"]        # Tiếng Anh
}

# Directory configuration (matching app.py)
MEDIA_FOLDER = 'media'
SHORT_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'short')
LONG_MEDIA_FOLDER = os.path.join(MEDIA_FOLDER, 'long')
TRASH_FOLDER = os.path.join(MEDIA_FOLDER, 'trash')

# Ensure directories exist
os.makedirs(SHORT_MEDIA_FOLDER, exist_ok=True)
os.makedirs(LONG_MEDIA_FOLDER, exist_ok=True)
os.makedirs(TRASH_FOLDER, exist_ok=True)

# Initialize translator
translator = Translator()

# Async TTS function
async def text_to_speech(text, voice, output_file, language):
    """Generate audio from text using the TTS model."""
    if language not in VALID_VOICES or voice not in VALID_VOICES[language]:
        # Fallback to default voice for the language
        voice = VALID_VOICES[language][0]
    tts = Communicate(text, voice)
    await tts.save(output_file)

# Sync wrapper for TTS
def run_tts(input_text, voice, save_path, language):
    """Run the TTS process synchronously."""
    asyncio.run(text_to_speech(input_text, voice, save_path, language))

# Function to translate text
def translate_text(text, source_lang, target_lang):
    """Translate text from source_lang to target_lang."""
    if source_lang == target_lang:
        return text
    try:
        translated = translator.translate(text, src=source_lang, dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

# Function to split text into chunks
def split_text_into_chunks(text, max_chunk_size=200):
    """Split text into chunks of approximately max_chunk_size, ensuring chunks end at the nearest sentence boundary (., \n)."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        boundary = max(text.rfind(".", start, end), text.rfind("\n", start, end))
        if boundary == -1:
            boundary = end
        chunks.append(text[start:boundary + 1].strip())
        start = boundary + 1
    return chunks

# Trong process_text_with_flow
def process_text_with_flow(text, voice, storage_folder, input_lang, output_lang):
    """Process text with enable_flow enabled."""
    # Translate text if needed
    processed_text = translate_text(text, input_lang, output_lang)
    timestamp = int(time.time())
    final_audio_filename = f"audio_{timestamp}.mp3"
    final_audio_path = os.path.join(storage_folder, final_audio_filename)

    # Split text into chunks and process in parallel
    chunks = split_text_into_chunks(processed_text)
    chunked_audio_files = []

    # Process each chunk in a separate thread
    threads = []
    for i, chunk in enumerate(chunks):
        chunk_filename = f"chunk_{timestamp}_{i}.mp3"
        chunk_path = os.path.join(TRASH_FOLDER, chunk_filename)
        thread = threading.Thread(target=run_tts, args=(chunk, voice, chunk_path, output_lang))
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

    return final_audio_filename, final_audio_path, processed_text

# Trong process_text_without_flow
def process_text_without_flow(text, voice, storage_folder, input_lang, output_lang):
    """Process text with enable_flow disabled."""
    # Translate text if needed
    processed_text = translate_text(text, input_lang, output_lang)
    timestamp = int(time.time())
    final_audio_filename = f"audio_{timestamp}.mp3"
    final_audio_path = os.path.join(storage_folder, final_audio_filename)

    # Process the entire text as a single audio file
    run_tts(processed_text, voice, final_audio_path, output_lang)

    return final_audio_filename, final_audio_path, processed_text
# Example usage
if __name__ == "__main__":
    # Test with English input, output in Vietnamese
    text_en = "Hello, this is a test."
    voice_vi = "vi-VN-HoaiMyNeural"
    input_lang = "en"
    output_lang = "vi"
    storage_folder = SHORT_MEDIA_FOLDER

    # Choose whether to use enable_flow or not
    enable_flow = True

    if enable_flow:
        final_audio_filename, final_audio_path = process_text_with_flow(
            text_en, voice_vi, storage_folder, input_lang, output_lang
        )
    else:
        final_audio_filename, final_audio_path = process_text_without_flow(
            text_en, voice_vi, storage_folder, input_lang, output_lang
        )

    print(f"Audio file generated: {final_audio_path}")

    # Test with Vietnamese input, output in English
    text_vi = "Xin chào, đây là một bài kiểm tra."
    voice_en = "en-US-JennyNeural"
    input_lang = "vi"
    output_lang = "en"

    if enable_flow:
        final_audio_filename, final_audio_path = process_text_with_flow(
            text_vi, voice_en, storage_folder, input_lang, output_lang
        )
    else:
        final_audio_filename, final_audio_path = process_text_without_flow(
            text_vi, voice_en, storage_folder, input_lang, output_lang
        )

    print(f"Audio file generated: {final_audio_path}")