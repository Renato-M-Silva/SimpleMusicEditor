from tkinter import ttk
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from threading import Thread
import subprocess

# --- Backend Logic (Download Logger) ---

class MyLogger:
    """Custom logger to capture yt-dlp output and display it in the GUI."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.is_downloading = False

    def debug(self, msg):
        if "ETA" in msg or "Downloading" in msg or "fragment" in msg or "progress" in msg:
            self.info(msg)
        else:
            self._log_message(msg)

    def warning(self, msg):
        self._log_message(f"[WARNING] {msg}")

    def error(self, msg):
        self._log_message(f"[ERROR] {msg}")

    def info(self, msg):
        if "Downloading" in msg and "ETA" in msg:
            if not self.is_downloading:
                self.is_downloading = True
                self._log_message("Starting download...")
            self._log_message(f"Downloading: {msg.split(' ')[1]} - ETA: {msg.split('ETA')[1].strip()}")
        elif "Destination" in msg:
            self.is_downloading = False
            self._log_message(f"Download complete: {msg.replace('[download] Destination: ', '')}")
        elif "[ExtractAudio]" in msg and "Destination" in msg:
            self._log_message("Audio extraction finished.")
        elif "[ffmpeg]" in msg and "Destination" in msg:
            self._log_message("Conversion to MP3 complete.")
        else:
            self._log_message(msg)
    
    def _log_message(self, msg):
        """Adds message to the text widget and scrolls to the end."""
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

def download_audio_logic(url, output_path, text_widget, parent_win):
    """Executes the download logic with parent window reference for dialogs."""
    my_logger = MyLogger(text_widget)
    base_path = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(base_path, "ffmpeg")


    # Define the path to the 'ffmpeg' folder inside your project
    base_path = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(base_path, "ffmpeg")

    ydl_opts = {
        'format': 'bestaudio/best',
        'cookiefile': 'youtubecookies.txt',
        'ffmpeg_location': ffmpeg_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'logger': my_logger,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # Use parent_win here for the messagebox
        messagebox.showinfo("Success", "Audio downloaded successfully!", parent=parent_win)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download audio: {e}", parent=parent_win)

def extract_audio_from_video(video_path, output_path, text_widget, parent_win):
    """Extracts audio from a local video file using ffmpeg."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(base_path, "ffmpeg")

        output_file = os.path.join(output_path, os.path.splitext(os.path.basename(video_path))[0] + ".mp3")

        cmd = [
            os.path.join(ffmpeg_path, "ffmpeg.exe"),
            "-i", video_path,
            "-vn",
            "-ac", "2",
            "-ar", "44100",
            "-b:a", "192k",
            output_file
        ]

        text_widget.insert(tk.END, "Extracting audio...\n")
        text_widget.update_idletasks()

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        messagebox.showinfo("Success", f"Audio extracted to:\n{output_file}", parent=parent_win)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract audio: {e}", parent=parent_win)


# --- GUI Component ---

def run_downloader(parent):
    """Launches the downloader window as a child of parent."""
    download_win = parent

    tk.Label(download_win, text="Select Source Type:").pack(pady=5)

    source_type = ttk.Combobox(download_win, values=["YouTube URL", "Local Video File"], state="readonly")
    source_type.current(0)
    source_type.pack(pady=5)

    tk.Label(download_win, text="Input:").pack(pady=5)
    input_entry = tk.Entry(download_win, width=60)
    input_entry.pack(pady=5)


    def start_process():
        mode = source_type.get()
        user_input = input_entry.get()

        path = filedialog.askdirectory(parent=download_win)
        if path:
            if mode == "YouTube URL":
                if user_input:
                    Thread(
                        target=download_audio_logic,
                        args=(user_input, path, progress_text, download_win),
                        daemon=True
                    ).start()
                else:
                    messagebox.showerror("Error", "Please enter a YouTube URL.", parent=download_win)
                    return

            elif mode == "Local Video File":
                video_file = filedialog.askopenfilename(
                    parent=download_win,
                    filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov"), ("All files", "*.*")]
                )

                if video_file:
                    Thread(
                        target=extract_audio_from_video,
                        args=(video_file, path, progress_text, download_win),
                        daemon=True
                    ).start()

    tk.Button(download_win, text="Start Process", command=start_process).pack(pady=10)
    progress_text = scrolledtext.ScrolledText(download_win, width=70, height=15)
    progress_text.pack(pady=5)