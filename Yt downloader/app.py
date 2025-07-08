import os
import re
import streamlit as st
from yt_dlp import YoutubeDL
from PIL import Image
import requests
from io import BytesIO

# Ensure downloads folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Sanitize filename
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|#🔥]', "_", title)

# Fetch video metadata
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['title'], info['formats'], info.get('thumbnail')

# Download and merge AV
def download_and_merge(url, format_id, title, tag, ext='mp4'):
    safe_title = sanitize_filename(title)
    output_file = f"downloads/{safe_title}_{tag}.{ext}"

    if os.path.exists(output_file):
        return output_file

    ydl_opts = {
        'format': format_id,
        'outtmpl': f"downloads/{safe_title}_{tag}.%(ext)s",
        'merge_output_format': ext,
        'quiet': True,
    }
    if ext == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for f in os.listdir('downloads'):
        if f.startswith(f"{safe_title}_{tag}") and not f.endswith(f".{ext}"):
            os.rename(os.path.join('downloads', f), output_file)
            break

    return output_file

# --------- Streamlit UI -----------
st.set_page_config(page_title="YouTube Downloader", layout="centered")

# Modern readable CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f1effc;
        font-family: 'Segoe UI', sans-serif;
        color: #222 !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #222 !important;
    }

    .stTextInput>div>div>input,
    .stTextArea>div>textarea {
        background-color: #fff;
        color: #111;
        border: 1px solid #ccc;
    }

    .stDownloadButton button {
        background-color: #6a1b9a;
        color: #fff !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }

    .stButton>button {
        background-color: #6a1b9a;
        color: #fff !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
    }

    .stSpinner {
        color: #333 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 YouTube Video Downloader")
st.markdown("Paste one or more YouTube URLs and click **Fetch** to select formats and download videos with audio. 🔊")

urls_input = st.text_area("Paste YouTube URLs (one per line)")
if st.button("🚀 Fetch Video Info") and urls_input.strip():
    urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]

    for url in urls:
        st.divider()
        st.subheader(f"🎥 Processing: {url}")
        with st.spinner("Fetching video details..."):
            try:
                title, formats, thumbnail = get_video_info(url)
                st.success(f"**Title:** {title}")

                if thumbnail:
                    response = requests.get(thumbnail)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        st.image(image, caption="Thumbnail", use_column_width=True)

                resolution_tabs = {
                    "360p": [],
                    "480p": [],
                    "720p": [],
                    "1080p": [],
                }
                audio_formats = []

                for fmt in formats:
                    height = fmt.get('height')
                    acodec = fmt.get('acodec')
                    vcodec = fmt.get('vcodec')

                    # ✅ Allow video-only formats (e.g., 1080p without audio)
                    if vcodec != 'none' and height:
                        if height in [360, 480, 720, 1080]:
                            key = f"{height}p"
                            resolution_tabs[key].append(fmt)
                    elif vcodec == 'none' and acodec != 'none':
                        audio_formats.append(fmt)

                tabs = st.tabs(list(resolution_tabs.keys()) + ["Audio Only"])

                for i, res in enumerate(["360p", "480p", "720p", "1080p"]):
                    with tabs[i]:
                        if not resolution_tabs[res]:
                            st.warning(f"No {res} formats available.")
                        for fmt in resolution_tabs[res]:
                            fmt_id = fmt['format_id']
                            ext = fmt['ext']
                            size = fmt.get('filesize') or 0
                            size_mb = round(size / (1024 * 1024), 2) if size else "Unknown"
                            tag = f"{res}_{ext}"
                            with st.spinner(f"Downloading {res}..."):
                                file_path = download_and_merge(url, fmt_id, title, tag)
                            st.markdown(f"**Format:** {ext.upper()}, **Size:** {size_mb} MB")
                            st.video(file_path)
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"⬇ Download {res} ({ext.upper()})",
                                    data=f,
                                    file_name=os.path.basename(file_path),
                                    mime="video/mp4",
                                    key=f"{res}_{ext}_{fmt_id}"  # ✅ Unique key
                                )

                with tabs[-1]:  # Audio Only tab
                    for fmt in audio_formats:
                        fmt_id = fmt['format_id']
                        ext = fmt['ext']
                        size = fmt.get('filesize') or 0
                        size_mb = round(size / (1024 * 1024), 2) if size else "Unknown"
                        tag = f"audio_{ext}"
                        with st.spinner("Downloading audio..."):
                            file_path = download_and_merge(url, fmt_id, title, tag, ext='mp3')
                        st.markdown(f"**Audio Format:** MP3, **Size:** {size_mb} MB")
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="🎵 Download Audio (MP3)",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="audio/mpeg",
                                key=f"audio_{fmt_id}"  # ✅ Unique key
                            )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
