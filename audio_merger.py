import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import os

# --- Robust Portable FFmpeg Configuration ---
base_path = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(base_path, "ffmpeg")

# Add the ffmpeg folder to the system PATH for this process
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Explicitly set the path for AudioSegment
AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")

# Verify the binaries actually exist
if not os.path.exists(AudioSegment.converter):
    print(f"CRITICAL: ffmpeg.exe not found at {AudioSegment.converter}")


def merge_tracks_logic(path1, path2, start1, end1, start2, end2, output_path, fade_ms):
    """Handles the audio processing logic."""
    try:
        # Convert seconds to milliseconds
        start1_ms, end1_ms = int(start1) * 1000, int(end1) * 1000
        start2_ms, end2_ms = int(start2) * 1000, int(end2) * 1000

        # Load files
        audio1 = AudioSegment.from_file(path1)
        audio2 = AudioSegment.from_file(path2)

        # Extract segments
        clip1 = audio1[start1_ms:end1_ms]
        clip2 = audio2[start2_ms:end2_ms]

        # Apply fades
        clip1 = clip1.fade_out(int(fade_ms))
        clip2 = clip2.fade_in(int(fade_ms))

        # Combine
        final_audio = clip1 + clip2

        # Export
        final_audio.export(output_path, format="mp3")
        messagebox.showinfo("Success", f"File saved to: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def run_merger(parent): # Accept parent window
    """Launches the merger window."""
    merger_win = parent # Make it a child of the main menu
    merger_win.title("Audio Merger")
    merger_win.geometry("400x450")

    # Inputs for Track 1
    tk.Label(merger_win, text="Track 1 Path:").pack()
    entry_path1 = tk.Entry(merger_win, width=50)
    entry_path1.pack()

    # PASS 'parent=merger_win' here! This ensures the file dialog is modal to the merger window, preventing it from being hidden behind other windows.
    tk.Button(merger_win, text="Browse", command=lambda: entry_path1.insert(0, filedialog.askopenfilename(parent=merger_win))).pack()

    # Inputs for Track 2
    tk.Label(merger_win, text="Track 2 Path:").pack()
    entry_path2 = tk.Entry(merger_win, width=50)
    entry_path2.pack()

    # PASS 'parent=merger_win' here!
    tk.Button(merger_win, text="Browse", command=lambda: entry_path2.insert(0, filedialog.askopenfilename(parent=merger_win))).pack()

    # Settings
    tk.Label(merger_win, text="Fade Duration (ms):").pack()
    entry_fade = tk.Entry(merger_win)
    entry_fade.insert(0, "2000")
    entry_fade.pack()

    def process():
        # PASS 'parent=merger_win' here too!
        output = filedialog.asksaveasfilename(parent=merger_win, defaultextension=".mp3")
        if output:
            merge_tracks_logic(
                entry_path1.get(), entry_path2.get(), 
                0, 10, 0, 10, # Placeholder values for time
                output, entry_fade.get()
            )

    tk.Button(merger_win, text="Merge and Save", command=process).pack(pady=20)