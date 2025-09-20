import re
import yt_dlp
import os
from openai import OpenAI
import json 
from dotenv import load_dotenv

def sanitize_filename(title):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', title)

def download_video(video_url=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',  # download template
    }

    url = video_url or input("Insira o link do vídeo do Instagram: ")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)

        # yt-dlp returns the final filename after post-processing
        if "requested_downloads" in info_dict:
            downloaded_file = info_dict["requested_downloads"][0]["filepath"]
        else:
            downloaded_file = info_dict.get("_filename", None)

        if not downloaded_file:
            raise RuntimeError("Não foi possível determinar o nome do arquivo baixado.")

        # Sanitize to ensure safe naming
        original_title = info_dict.get('title', 'video')
        safe_title = sanitize_filename(original_title)
        mp3_filename = f"{safe_title}.mp3"

        if downloaded_file != mp3_filename:
            os.rename(downloaded_file, mp3_filename)

    return mp3_filename

def transcribe_audio_portuguese(filename):
    # Load .env file
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI(api_key=api_key)

    with open(filename, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pt"
        )
    # Delete the audio file after transcription
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Erro ao deletar o arquivo de áudio: {e}")

    return response.text



if __name__ == "__main__":
    audio_file = download_video()
    transcription = transcribe_audio_portuguese(audio_file)
    print("Transcrição:\n", transcription)
