import tkinter as tk
import os
import warnings

# --- Robust Portable FFmpeg Configuration ---
base_path = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(base_path, "ffmpeg")
# Add the ffmpeg folder to the system PATH for this process
os.environ["PATH"] += os.pathsep + ffmpeg_path

# importing pydub after setting the PATH to ensure it can find ffmpeg
from pydub import AudioSegment
AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")

# Verify the binaries actually exist
if not os.path.exists(AudioSegment.converter):
    print(f"CRITICAL: ffmpeg.exe not found at {AudioSegment.converter}")
if not os.path.exists(AudioSegment.ffprobe):
    print(f"CRITICAL: ffprobe.exe not found at {AudioSegment.ffprobe}")

from modules import downloader, merger

# Suppress specific warnings from pydub/ffmpeg
warnings.filterwarnings("ignore", category=RuntimeWarning)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SME - Simple Music Editor")
        # Set a minimum size for the window
        self.minsize(400, 200)

        # Make window responsive
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create a container frame to hold the current view (menu, downloader, merger)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Make the container responsive
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.show_menu()

    def clear_container(self):
        # Remove everything in the container
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_container()
        tk.Label(self.container, text="Main Menu", font=("Arial", 14)).pack(pady=20)
        tk.Button(self.container, text="YouTube Downloader", command=self.open_downloader).pack(pady=5)
        tk.Button(self.container, text="Audio Merger", command=self.open_merger).pack(pady=5)
        tk.Button(self.container, text="Exit", command=self.quit).pack(pady=5)

    def open_downloader(self):
        # Back button to return to the main menu
        tk.Button(self.container, text="← Back to Menu", command=self.show_menu).pack(anchor="nw", padx=10, pady=5)
        # Pass the container to run_downloader to draw within it
        downloader.run_downloader(self.container)

    def open_merger(self):
        self.clear_container()
        # Back button to return to the main menu
        tk.Button(self.container, text="← Back to Menu", command=self.show_menu).pack(anchor="nw", padx=10, pady=5)
        # Pass the container to audio_merger to draw within it
        merger.run_merger(self.container)

if __name__ == "__main__":
    app = App()
    app.mainloop()