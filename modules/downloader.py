import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from threading import Thread

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

# --- GUI Component ---

def run_downloader(parent):
    """Launches the downloader window as a child of parent."""
    download_win = parent

    tk.Label(download_win, text="YouTube URL:").pack(pady=5)
    url_entry = tk.Entry(download_win, width=60)
    url_entry.pack(pady=5)

    def start_process():
        url = url_entry.get()
        # PASS 'parent=download_win' here to keep focus!
        path = filedialog.askdirectory(parent=download_win)
        if url and path:
            Thread(target=download_audio_logic, args=(url, path, progress_text, download_win), daemon=True).start()

    tk.Button(download_win, text="Download", command=start_process).pack(pady=10)
    progress_text = scrolledtext.ScrolledText(download_win, width=70, height=15)
    progress_text.pack(pady=5)