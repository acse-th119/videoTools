# 🎬 videoTools

A simple yet powerful web-based tool for downloading videos, extracting subtitles, and converting videos to audio — all powered by [Gradio](https://gradio.app/) and `yt-dlp`.

## 🧰 Features

- 📥 **Video Download**  
  Paste a video URL and download videos directly from supported platforms (YouTube, BiliBili, etc.).

- 💬 **Subtitle Download**  
  Download subtitles in a selected language. If unsure about available subtitle languages, run without input to see suggestions.

- 🎧 **Video to Audio Conversion**  
  Upload a video file and convert it to an `.mp3` audio file using `ffmpeg`.

## 🚀 Quick Start

### 📦 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/<your-username>/videoTools.git
cd videoTools
conda activate videoTools
pip install -r requirements.txt
```

### ▶️ Run Locally
```bash
python mainui.py
```
Then visit http://localhost:7861 in your browser.

### 🐳 Docker Usage
Build and run with Docker:

```bash
docker build -t gr-video-tool .
docker run -p 7860:7860 -v $(pwd)/downloads:/app/downloads gr-video-tool
Push to Docker Hub:
```

```bash
docker tag gr-video-tool caesarhtx/gr-video-tool
docker push caesarhtx/gr-video-tool
```
📂 Project Structure
```bash
videoTools/
├── mainui.py               # Gradio UI main app
├── VideoFetcher.py         # Handles video and subtitle fetching
├── VideoUtils.py           # Utility functions (e.g. latest file fetch)
├── whisperUI.py            # (Optional) Integration with Whisper
├── StreamingLogger.py      # Log streaming
├── downloads/              # Downloaded video and subtitle files
├── README.md
├── requirements.txt
└── Dockerfile
```
## 🛠️ Notes
Uses yt-dlp under the hood, which supports a wide variety of video platforms.

ffmpeg must be installed and available in your system's PATH for audio conversion.

Subtitle formats can optionally be converted to .txt.

## 🤝 Contributing
Pull requests welcome! Please make sure your code is well-documented.

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.