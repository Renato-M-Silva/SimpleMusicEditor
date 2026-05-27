# Simple Music Editor (SME)

A modular, portable Python application to download audio from YouTube and merge audio files with custom fade effects.

## Features
- **YouTube Downloader:** Downloads and converts YouTube videos to MP3.
- **Audio Merger:** Combines two audio tracks with configurable cross-fades.
- **Portable Design:** Encapsulated FFmpeg binaries for cross-machine compatibility.

## Prerequisites
- Python 3.11+
- [FFmpeg](https://ffmpeg.org/download.html) (Required for audio processing)

## Setup
1. Clone this repository:
   ```bash
   git clone [https://github.com/Renato-M-Silva/SimpleMusicEditor.git](https://github.com/Renato-M-Silva/SimpleMusicEditor.git)
   cd SimpleMusicEditor
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Important:  
Place ffmpeg.exe and ffprobe.exe inside a folder named ffmpeg at the root of the project. (These files are excluded from the repository due to size limits).

## How to Run
Run the main menu:

   ```bash
   python SME.py
   ```

## Project Structure

- SME.py: Main entry point and GUI menu.

- Youtube2Mp3.py: Module for downloading/converting audio.

- audio_merger.py: Module for merging and processing audio.

- ffmpeg/: Directory for required FFmpeg binaries.


---

> [!NOTE]
> Note to self: To run this project, ensure ffmpeg.exe and ffprobe.exe are placed inside the ffmpeg/ folder. They are excluded from the repository due to size limits.