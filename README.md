# Simple Music Editor (SME)

A modular, portable Python application to download audio from YouTube and merge audio files with custom fade effects.

## Features
- **Centralized Menu:** Intuitive navigation between tools within a single window.
- **YouTube Downloader:** Downloads and converts YouTube videos to MP3.
- **Audio Merger:** Combines two audio tracks with configurable cross-fades.
- - Precise start/end time configuration.
- - Real-time segment and fade preview.
- - Custom Transition Modes: Choose between Crossfade, Fade Out/In, or Transition Sound Injection.
- **Portable Architecture:** Designed to use local FFmpeg binaries from the /ffmpeg directory, ensuring consistent behavior across different environments.

## Project Structure

```
SimpleMusicEditor/
├── SME.py               # Main entry point and GUI controller
├── modules/             # Application modules
│   ├── downloader.py    # Download logic
│   └── merger.py        # Audio processing and merging logic
├── ffmpeg/              # Required FFmpeg binaries (ffmpeg.exe, ffprobe.exe)
├── requirements.txt     # Project dependencies
├── README.md
└── LICENSE
```

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
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. FFmpeg Setup:  
Since the binaries are excluded from the repository due to size limits, download them from the [official website](https://ffmpeg.org/download.html) and place ffmpeg.exe and ffprobe.exe inside the /ffmpeg folder in the project root.

## How to Run
Run the main menu:

   ```bash
   python SME.py
   ```
  

## Transition Modes Explained
- **Crossfade:** Overlaps the end of Track 1 with the start of Track 2 for a seamless musical blend.

- **Fade Out/In:** Gradually mutes Track 1 and then introduces Track 2, ensuring no overlap.

- **Transition Sound:** Allows you to insert a custom audio file (e.g., sound effects, transitions) between the two main tracks.

---
  
> [!NOTE]
> Note to self: To run this project, ensure ffmpeg.exe and ffprobe.exe are placed inside the ffmpeg/ folder. They are excluded from the repository due to size limits.