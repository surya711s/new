import sys
import subprocess

def download_video(video_url):
    try:
        # Download best quality video+audio
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            video_url
        ], check=True)
    except subprocess.CalledProcessError:
        print("Download failed. Please verify the URL.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        download_video(sys.argv[1])
    else:
        print("No URL provided.")