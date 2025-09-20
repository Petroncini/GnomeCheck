import re
import yt_dlp
import os

def sanitize_filename(title):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', title)

def download_instagram_video(video_url):
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
        original_title = info_dict.get('title', 'video')
        safe_title = sanitize_filename(original_title)
        mp3_filename = f"{safe_title}.mp3"

        # The file already exists as '<original_title>.mp3', rename it if needed
        downloaded_file = f"{original_title}.mp3"
        if downloaded_file != mp3_filename:
            os.rename(downloaded_file, mp3_filename)

    return mp3_filename

def transcribe_audio_portuguese(filename):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(filename, language="pt")  # force Portuguese
    print("Transcrição:\n", result["text"])

if __name__ == "__main__":
    audio_file = download_instagram_video()
    transcribe_audio_portuguese(audio_file)
