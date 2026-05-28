import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import os
import sounddevice as sd
import numpy as np

class AudioPlayer:
    """Simple audio player using sounddevice for low-latency playback"""
    def __init__(self):
        self.stream = None

    def play_segment(self, audio_segment):
        """Plays a Pydub AudioSegment using sounddevice."""
        # Convert Pydub AudioSegment to raw data
        # Get raw data as a numpy array
        samples = np.array(audio_segment.get_array_of_samples())
        
        # Handle stereo/mono
        if audio_segment.channels == 2:
            samples = samples.reshape((-1, 2))
            
        # Normalize to float32 for sounddevice
        samples = samples.astype(np.float32) / (1 << (8 * audio_segment.sample_width - 1))
        
        # Play the array directly from RAM
        sd.play(samples, samplerate=audio_segment.frame_rate)

    def is_playing(self):
        return sd.get_stream().active

    def stop(self):
        sd.stop()

def run_merger(parent):
    """Sets up the audio merger GUI and functionality."""
    # Set up the merger window
    merger_win = parent

    player = AudioPlayer()

    def on_play_click(audio, btn_play, btn_stop):
        """Plays the given audio segment and manages button states."""
        player.play_segment(audio)
        btn_play.config(state="disabled") # Disable Play
        btn_stop.config(state="normal")   # Enable Stop
        monitor_playback(btn_play, btn_stop) # Start monitoring to reset buttons when audio finishes

    def on_stop_click(btn_play, btn_stop):
        """Stops playback and resets button states."""
        player.stop()
        btn_stop.config(state="disabled") # Disable Stop
        btn_play.config(state="normal")   # Enable Play

    def monitor_playback(btn_play, btn_stop):
        """Checks if audio is still playing and resets buttons when done."""
        if not player.is_playing():
            # Audio finished, reset the buttons
            on_stop_click(btn_play, btn_stop)
        else:
            # Still playing, check again in 100ms
            merger_win.after(100, lambda: monitor_playback(btn_play, btn_stop))

    global_audio_merged = None  # This will hold the merged audio object

    def load_track_info(path, label_info):
        """Calculates and displays audio info."""
        try:
            audio = AudioSegment.from_file(path)
            duration_sec = len(audio) / 1000
            file_size = os.path.getsize(path) / (1024 * 1024)
            label_info.config(text=f"Size: {file_size:.2f} MB | Duration: {duration_sec:.2f}s")
            return audio
        except Exception as e:
            label_info.config(text="Error loading file")
            return None

    def create_track_section(parent_win, label_text):
        """Creates a section in the GUI for selecting and controlling an audio track."""
        # Container for the whole section
        section = tk.LabelFrame(parent_win, text=label_text, padx=10, pady=10)
        section.pack(fill="x", padx=10, pady=5)

        # Row 1: Path and Browse
        row1 = tk.Frame(section)
        row1.pack(fill="x")
        entry = tk.Entry(row1, width=50)
        entry.pack(side=tk.LEFT, expand=True, fill="x")
        btn_browse = tk.Button(row1, text="Browse", command=lambda: setup_browser(merger_win,entry, btn_play, btn_stop, label_info))
        btn_browse.pack(side=tk.LEFT)

        # Row 2: Info (Size/Duration)
        label_info = tk.Label(section, text="Select a file to see details...", fg="blue")
        label_info.pack(fill="x", pady=5)

        # Row 3: Controls
        row3 = tk.Frame(section)
        row3.pack(fill="x")
        btn_play = tk.Button(row3, text="▶", state="disabled")
        btn_stop = tk.Button(row3, text="■", state="disabled", command=lambda: on_stop_click(btn_play, btn_stop))
        
        tk.Label(row3, text="Start(s):").pack(side=tk.LEFT)
        entry_start = tk.Entry(row3, width=5)
        entry_start.insert(0, "0")
        entry_start.pack(side=tk.LEFT)
        tk.Label(row3, text="End(s):").pack(side=tk.LEFT)
        entry_end = tk.Entry(row3, width=5)
        entry_end.pack(side=tk.LEFT)
        
        btn_play.pack(side=tk.LEFT)
        btn_stop.pack(side=tk.LEFT)
        
        return entry, btn_browse, btn_play, btn_stop, entry_start, entry_end, label_info

    def setup_browser(parent_win, entry, btn_play, btn_stop, label_info):
        """Handles the file browsing and loading of audio info."""
        # Open file dialog and load audio info
        file = filedialog.askopenfilename(parent=parent_win, filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")], title="Select an audio file")
        if file:
            entry.delete(0, tk.END)
            entry.insert(0, file)
            audio = load_track_info(file, label_info)
            if audio:
                btn_play.config(state="normal", command=lambda: on_play_click(audio, btn_play, btn_stop))

    # Create sections
    e1, b1, p1, s1, st1, en1, inf1 = create_track_section(merger_win, "Track 1")
    e2, b2, p2, s2, st2, en2, inf2 = create_track_section(merger_win, "Track 2")


    def merge_tracks():
        """Merges the selected audio tracks based on user-defined start/end times."""
        # Merge the selected audio tracks
        nonlocal global_audio_merged
        try:
            audio1 = AudioSegment.from_file(e1.get())
            audio2 = AudioSegment.from_file(e2.get())
            
            # Get start/end times
            start1 = float(st1.get()) * 1000
            end1 = float(en1.get()) * 1000 if en1.get() else len(audio1)
            start2 = float(st2.get()) * 1000
            end2 = float(en2.get()) * 1000 if en2.get() else len(audio2)
            
            # Extract segments
            seg1 = audio1[start1:end1]
            seg2 = audio2[start2:end2]
            
            # Merge (concatenate)
            global_audio_merged = seg1 + seg2
            btn_play_merged.config(state="normal")
            btn_save.config(state="normal")
            
            messagebox.showinfo("Success", "Tracks merged successfully!", parent=merger_win)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge tracks: {e}", parent=merger_win)

    # Set up browse buttons
    tk.Button(merger_win, text="Merge Tracks", command=merge_tracks).pack(pady=10)
    btn_play_merged = tk.Button(merger_win, text="▶ Play Merged", state="disabled", command=lambda: on_play_click(global_audio_merged, btn_play_merged, btn_stop_merged))
    btn_play_merged.pack(pady=5)
    btn_stop_merged = tk.Button(merger_win, text="■ Stop", state="disabled", command=lambda: on_stop_click(btn_play_merged, btn_stop_merged))
    btn_stop_merged.pack(pady=5)

    def save_merged(parent_win):
        """Saves the merged audio to a user-selected file location."""
        # Save the merged audio to a file
        if global_audio_merged:
            save_path = filedialog.asksaveasfilename(parent=parent_win, defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
            if save_path:
                try:
                    global_audio_merged.export(save_path, format="mp3")
                    messagebox.showinfo("Saved", f"Merged audio saved to {save_path}", parent=parent_win)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}", parent=parent_win)

    # Save button for merged audio
    btn_save = tk.Button(merger_win, text="💾 Save Merged", state="disabled", command=lambda: save_merged(merger_win))
    btn_save.pack(pady=5)

