import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
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
    
    def get_segment(audio_segment, start_entry, end_entry, fade_entry=None, apply_fade=False):
        start_ms = float(start_entry.get() or 0) * 1000
        end_ms = float(end_entry.get()) * 1000 if end_entry.get() else len(audio_segment)
        
        segment = audio_segment[start_ms:end_ms]
        
        if apply_fade:
            fade_ms = int(fade_entry.get() or 1000)
            segment = segment.fade_in(fade_ms).fade_out(fade_ms)
            
        return segment

    def on_play_click(audio, btn_play,btn_stop, btn_seg=None, btn_fade=None):
        """Plays the given audio segment and manages button states."""
        player.play_segment(audio)
        btn_play.config(state="disabled") # Disable Play
        btn_stop.config(state="normal")   # Enable Stop

        if btn_seg:
            btn_seg.config(state="disabled")  # Disable Segment
        if btn_fade:
            btn_fade.config(state="disabled") # Disable Fade

        monitor_playback(btn_play, btn_stop, btn_seg, btn_fade) # Start monitoring to reset buttons when audio finishes

    def on_stop_click(btn_play, btn_stop, btn_seg=None, btn_fade=None):
        """Stops playback and resets button states."""
        player.stop()
        btn_stop.config(state="disabled") # Disable Stop
        btn_play.config(state="normal")   # Enable Play
        if btn_seg:
            btn_seg.config(state="normal")    # Enable Segment
        if btn_fade:
            btn_fade.config(state="normal")   # Enable Fade

    def monitor_playback(btn_play, btn_stop, btn_seg=None, btn_fade=None):
        """Checks if audio is still playing and resets buttons when done."""
        if not player.is_playing():
            # Audio finished, reset the buttons
            on_stop_click(btn_play, btn_stop, btn_seg, btn_fade)
        else:
            # Still playing, check again in 100ms
            merger_win.after(100, lambda: monitor_playback(btn_play, btn_stop, btn_seg, btn_fade))

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
        btn_browse = tk.Button(row1, text="Browse", command=lambda: setup_browser(merger_win,entry, btn_play, btn_stop, btn_seg, btn_fade, entry_start, entry_end, label_info, entry_fade))
        btn_browse.pack(side=tk.LEFT)

        # Row 2: Info (Size/Duration)
        label_info = tk.Label(section, text="Select a file to see details...", fg="blue")
        label_info.pack(fill="x", pady=5)

        # Row 3: Controls
        row3 = tk.Frame(section)
        row3.pack(fill="x")
        btn_play = tk.Button(row3, text="▶", state="disabled")
        btn_seg = tk.Button(row3, text="▶ Segment", state="disabled")
        btn_fade = tk.Button(row3, text="▶ Fade", state="disabled")
        btn_stop = tk.Button(row3, text="■", state="disabled", command=lambda: on_stop_click(btn_play, btn_stop, btn_seg, btn_fade))
        

        tk.Label(row3, text="Start(s):").pack(side=tk.LEFT)
        entry_start = tk.Entry(row3, width=5)
        entry_start.insert(0, "0")
        entry_start.pack(side=tk.LEFT)
        tk.Label(row3, text="End(s):").pack(side=tk.LEFT)
        entry_end = tk.Entry(row3, width=5)
        entry_end.pack(side=tk.LEFT)
        
        tk.Label(row3, text="Fade(ms):").pack(side=tk.LEFT)
        entry_fade = tk.Entry(row3, width=5)
        entry_fade.insert(0, "500") # default fade duration  
        entry_fade.pack(side=tk.LEFT)

        btn_play.pack(side=tk.LEFT)
        btn_seg.pack(side=tk.LEFT)
        btn_fade.pack(side=tk.LEFT)
        btn_stop.pack(side=tk.LEFT)
        
        return entry, btn_browse, btn_play, btn_stop, entry_start, entry_end, label_info, entry_fade

    def setup_browser(parent_win, entry, btn_play, btn_stop, btn_seg, btn_fade, entry_start, entry_end, label_info, entry_fade):
        """Handles the file browsing and loading of audio info."""
        # Open file dialog and load audio info
        file = filedialog.askopenfilename(parent=parent_win, filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")], title="Select an audio file")
        if file:
            entry.delete(0, tk.END)
            entry.insert(0, file)
            audio = load_track_info(file, label_info)
            if audio:
                btn_play.config(state="normal", command=lambda: on_play_click(audio, btn_play, btn_stop, btn_seg, btn_fade ))
                # Play Full
                btn_play.config(state="normal", command=lambda: on_play_click(audio, btn_play, btn_stop, btn_seg, btn_fade))
                # Play Segment
                btn_seg.config(state="normal", command=lambda: on_play_click(get_segment(audio, entry_start, entry_end, False), btn_play, btn_stop, btn_seg, btn_fade ))
                # Play Fade
                btn_fade.config(state="normal", command=lambda: on_play_click(get_segment(audio, entry_start, entry_end, entry_fade, True), btn_play, btn_stop, btn_seg, btn_fade ))

                btn_stop.config(state="normal")

    # Create sections
    e1, b1, p1, s1, st1, en1, inf1, f1 = create_track_section(merger_win, "Track 1")
    e2, b2, p2, s2, st2, en2, inf2, f2  = create_track_section(merger_win, "Track 2")
    fade = f2  # Use fade entry from second track for crossfade duration

    def merge_tracks(crossfade_ms=500):
        """Merges the selected audio tracks based on user-defined start/end times."""
        # Merge the selected audio tracks
        nonlocal global_audio_merged
        tipo = combo_transition.get()

        try:
            crossfade_ms = int(crossfade_ms)
        except:
            crossfade_ms = 0

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
            if tipo == "Crossfade":
                global_audio_merged = seg1.append(seg2, crossfade=crossfade_ms)
                
            elif tipo == "Fade Out/In":
                # Fade out na 1, fade in na 2, sem sobreposição
                seg1_fade = seg1.fade_out(crossfade_ms)
                seg2_fade = seg2.fade_in(crossfade_ms)
                global_audio_merged = seg1_fade + seg2_fade
                
            elif tipo == "Insert Sound (Transition)":
                # Asks user to select a transition sound, then concatenates: End of 1 + Transition Sound + Start of 2
                sound_transition_path = filedialog.askopenfilename(title="Select the transition sound")
                if sound_transition_path:
                    sound_transition = AudioSegment.from_file(sound_transition_path)
                    # Concatenate: End of seg1 + Transition Sound + Start of seg2
                    global_audio_merged = seg1 + sound_transition + seg2
            btn_play_merged.config(state="normal")
            btn_save.config(state="normal")
            
            messagebox.showinfo("Success", "Tracks merged successfully!", parent=merger_win)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge tracks: {e}", parent=merger_win)

    # Row 2: Info (Size/Duration)
    label_info = tk.Label(text="Merger will happen using fade from second track", fg="black")
    label_info.pack(fill="x", pady=5)
    # Set up browse buttons
    tk.Button(merger_win, text="Merge Tracks", command=lambda: merge_tracks(crossfade_ms=int(fade.get()))).pack(pady=10)
    btn_play_merged = tk.Button(merger_win, text="▶ Play Merged", state="disabled", command=lambda: on_play_click(global_audio_merged, btn_play_merged, btn_stop_merged))
    btn_play_merged.pack(pady=5)
    btn_stop_merged = tk.Button(merger_win, text="■ Stop", state="disabled", command=lambda: on_stop_click(btn_play_merged, btn_stop_merged))
    btn_stop_merged.pack(pady=5)

    tk.Label(merger_win, text="Tipo de Transição:").pack(pady=5)
    combo_transition = ttk.Combobox(merger_win, values=["Crossfade", "Fade Out/In", "Insert Sound (Transition)"], state="readonly")
    combo_transition.current(0) # Seleciona Crossfade por padrão
    combo_transition.pack(pady=5)

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

