from email.mime import audio
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
        self.samples = None
        self.position = 0

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
        
        # removed sd.play() in favor of using OutputStream for better control and to avoid issues with multiple play calls
        ## Play the array directly from RAM
        # sd.play(samples, samplerate=audio_segment.frame_rate)

        # Stop previous stream if any
        if self.stream:
            self.stream.stop()
            self.stream.close()

        # Store samples for callback
        self.samples = samples
        self.position = 0
        self.samplerate = audio_segment.frame_rate
        
        # Callback function
        def callback(outdata, frames, time, status):
            # Check if we have samples to play
            if self.samples is None:
                outdata[:] = 0
                raise sd.CallbackStop()
            
            # Calculate how many samples to output
            end = self.position + frames
            chunk = self.samples[self.position:end]

            # If we've reached the end of the samples, stop playback
            if len(chunk) == 0:
                outdata[:] = 0
                raise sd.CallbackStop()
            
            # If we have less samples than requested, pad with zeros
            elif len(chunk) < frames:
                # End of audio
                outdata[:len(chunk)] = chunk
                outdata[len(chunk):] = 0
                self.position = end
                raise sd.CallbackStop()
            else:
                outdata[:] = chunk
                self.position = end

        # Create non-blocking stream
        self.stream = sd.OutputStream(
            samplerate=audio_segment.frame_rate,
            channels=audio_segment.channels,
            dtype='float32',
            callback=callback,
            blocksize=1024  # smaller blocksize for lower latency
        )

        self.stream.start()

    def is_playing(self):
        # Check if the stream is active (playing)
        # Note: sounddevice does not provide a direct way to check if audio is still playing, but we can check if the stream is active.
        # removed sd.get_stream().active in favor of checking self.stream to avoid issues when no stream is initialized
        # return sd.get_stream().active
        # We check if self.stream exists and is active to avoid errors when no stream is initialized
        return self.stream is not None and self.stream.active

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.samples = None
            self.position = 0

def run_merger(parent):
    """Sets up the audio merger GUI and functionality."""
    # Set up the merger window
    merger_win = parent

    # Two main columns
    left_column = tk.Frame(merger_win)
    right_column = tk.Frame(merger_win)

    left_column.pack(side="left", fill="both", expand=True)
    right_column.pack(side="right", fill="both", expand=True)


    player = AudioPlayer()
    
    # Helper function to extract segment with optional fade (not currently used, but can be used for the "Play Segment" button if we want to apply fade on the fly)
    # def get_segment(audio_segment, start_entry, end_entry, fade_entry=None, apply_fade=False):
    #     """Extracts a segment from the audio based on start/end times and applies fade if specified."""
    #     start_ms = float(start_entry.get() or 0) * 1000
    #     end_ms = float(end_entry.get()) * 1000 if end_entry.get() else len(audio_segment)
    #    
    #    segment = audio_segment[start_ms:end_ms]
    #    
    #    if apply_fade:
    #        fade_ms = int(fade_entry.get() or 1000)
    #        segment = segment.fade_in(fade_ms).fade_out(fade_ms)
    #        
    #    return segment

    def on_play_click(audio, btn_play,btn_stop, btn_seg=None, btn_fade=None, slider=None):
        """Plays the given audio segment and manages button states."""
        # If a slider is provided, start from the slider's position
        start_ms = getattr(slider, "seek_offset", 0)

        # Cut audio only when PLAY is pressed
        audio_to_play = audio[start_ms:]
        player.play_segment(audio_to_play)
        if slider:
            monitor_slider(slider, audio, start_ms)  # Start monitoring slider position

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

    def monitor_slider(slider, audio_segment, offset=0):
        """Updates the slider position while audio is playing."""
        if player.is_playing():
            # position is in frames; convert to milliseconds
            pos_ms = int(player.position / player.samplerate * 1000)

            slider.set(offset + pos_ms)
            merger_win.after(50, lambda: monitor_slider(slider, audio_segment, offset))  

    def monitor_slider_segment(slider, audio_segment, start_ms, end_ms, btn_play=None, btn_stop=None, btn_seg=None):
        if player.is_playing():
            # Calculate position
            pos_ms = start_ms + int(player.position / player.samplerate * 1000)

            # Update slider
            slider.set(pos_ms)

            # Stop exactly at the end
            if pos_ms >= end_ms:
                player.stop()
                slider.set(end_ms)

                # Reset buttons
                on_stop_click(btn_play, btn_stop, btn_seg)
                return

            merger_win.after(50, lambda: monitor_slider_segment(slider, audio_segment, start_ms, end_ms, btn_play, btn_stop, btn_seg))

    def on_slider_release(event, audio_segment, slider, btn_play, btn_stop, btn_seg=None):
        """Slider only selects the position. Does NOT start playback."""
        # Save the selected position (in ms)
        slider.seek_offset = slider.get()

    def play_segment_with_slider(audio_segment, start_ms, end_ms, btn_play, btn_stop, btn_seg, slider):
        """Play only a segment and stop exactly at the end."""
        # Save segment boundaries
        slider.seek_offset = start_ms
        slider.segment_end = end_ms

        # Move slider to the start
        slider.set(start_ms)

        # Cut audio only for playback
        audio_to_play = audio_segment[start_ms:end_ms]

        # Play
        player.play_segment(audio_to_play)

        # Start monitoring
        monitor_slider_segment(slider, audio_segment, start_ms, end_ms, btn_play, btn_stop, btn_seg)

        # Update buttons
        btn_play.config(state="disabled")
        btn_stop.config(state="normal")
        btn_seg.config(state="disabled")


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
        btn_browse = tk.Button(row1, text="Browse", command=lambda: setup_browser(merger_win,entry, btn_play, btn_stop, btn_seg, entry_start, entry_end, label_info, slider))
        btn_browse.pack(side=tk.LEFT)

        # Row 2: Info (Size/Duration)
        label_info = tk.Label(section, text="Select a file to see details...", fg="blue")
        label_info.pack(fill="x", pady=5)

        # Row 3: Controls
        row3 = tk.Frame(section)
        row3.pack(fill="x")
        btn_play = tk.Button(row3, text="▶", state="disabled")
        btn_seg = tk.Button(row3, text="▶ Segment", state="disabled")
        btn_stop = tk.Button(row3, text="■", state="disabled", command=lambda: on_stop_click(btn_play, btn_stop, btn_seg))
        

        tk.Label(row3, text="Start(s):").pack(side=tk.LEFT)
        entry_start = tk.Entry(row3, width=5)
        entry_start.insert(0, "0")
        entry_start.pack(side=tk.LEFT)
        tk.Label(row3, text="End(s):").pack(side=tk.LEFT)
        entry_end = tk.Entry(row3, width=5)
        entry_end.pack(side=tk.LEFT)
        

        btn_play.pack(side=tk.LEFT)
        btn_seg.pack(side=tk.LEFT)
        btn_stop.pack(side=tk.LEFT)

        # Row 4: Position slider
        slider = tk.Scale(
            section,
            from_=0,
            to=1000,  # temporary value, updated when audio loads
            orient="horizontal",
            length=400,
            label="Position (ms)"
        )
        slider.pack(fill="x", pady=5)
        
        return entry, btn_browse, btn_play, btn_stop, entry_start, entry_end, label_info, slider

    def setup_browser(parent_win, entry, btn_play, btn_stop, btn_seg, entry_start, entry_end, label_info, slider):
        """Handles the file browsing and loading of audio info."""
        # Open file dialog and load audio info
        file = filedialog.askopenfilename(parent=parent_win, filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")], title="Select an audio file")
        if file:
            entry.delete(0, tk.END)
            entry.insert(0, file)
            audio = load_track_info(file, label_info)
            
            if audio:
                # Update slider range based on audio duration
                slider.config(to=len(audio))
                slider.set(0)
                
                # Bind slider release event
                slider.bind("<ButtonRelease-1>", lambda e: on_slider_release(e, audio, slider, btn_play, btn_stop, btn_seg))

                # Play Full Track
                btn_play.config(state="normal", command=lambda: on_play_click(audio, btn_play, btn_stop, btn_seg, None, slider))
                # Play Segment with optional fade
                # change to use play_segment_with_slider which will stop exactly at the end of the segment and update the slider accordingly
                # btn_seg.config(state="normal", command=lambda: on_play_click(get_segment(audio, entry_start, entry_end, False), btn_play, btn_stop, btn_seg, None, slider))
                btn_seg.config(
                    state="normal",
                    command=lambda: play_segment_with_slider(
                        audio,
                        int(float(entry_start.get() or 0) * 1000),
                        int(float(entry_end.get() or len(audio)/1000) * 1000),
                        btn_play,
                        btn_stop,
                        btn_seg,
                        slider
                    )
                )

                # Stop 
                btn_stop.config(state="normal")
                


    # Create sections
    e1, b1, p1, s1, st1, en1, inf1, slider1= create_track_section(left_column, "Track 1")
    e2, b2, p2, s2, st2, en2, inf2, slider2 = create_track_section(left_column, "Track 2")
    

    def merge_tracks(entry_fade_out=None, entry_fade_in=None):
        """Merges the selected audio tracks based on user-defined start/end times."""
        # Merge the selected audio tracks
        nonlocal global_audio_merged
        tipo = combo_transition.get()

        try:
            audio1 = AudioSegment.from_file(e1.get())
            audio2 = AudioSegment.from_file(e2.get())
            # Ensure both audio segments have the same frame rate and channels for proper merging
            audio1 = audio1.set_frame_rate(44100).set_channels(2)
            audio2 = audio2.set_frame_rate(44100).set_channels(2)

            
            # Get start/end times
            start1 = float(st1.get()) * 1000 if st1.get() else 0
            end1 = float(en1.get()) * 1000 if en1.get() else len(audio1)
            start2 = float(st2.get()) * 1000 if st2.get() else 0
            end2 = float(en2.get()) * 1000 if en2.get() else len(audio2)
            
            # Extract segments
            seg1 = audio1[start1:end1]
            seg2 = audio2[start2:end2]
            
            # Merge (concatenate)
            if tipo == "Crossfade":
                global_audio_merged = seg1.append(seg2, crossfade=int(entry_fade_in.get()))
                
            elif tipo == "Fade Out/In":
                # Fade out seg1 and fade in seg2, then concatenate without overlap
                seg1_fade = seg1.fade_out(int(entry_fade_out.get()))
                seg2_fade = seg2.fade_in(int(entry_fade_in.get()))
                global_audio_merged = seg1_fade + seg2_fade
                
            elif tipo == "Insert Sound (Transition)":
                # Asks user to select a transition sound, then concatenates: End of 1 + Transition Sound + Start of 2
                sound_transition_path = filedialog.askopenfilename(title="Select the transition sound")
                if sound_transition_path:
                    sound_transition = AudioSegment.from_file(sound_transition_path)
                    # Apply fade to the transition sound if specified
                    if entry_fade_in.get() and entry_fade_out.get():
                        sound_transition = sound_transition.fade_in(int(entry_fade_in.get())).fade_out(int(entry_fade_out.get())) 
                        seg1_fade = seg1.fade_out(int(entry_fade_out.get()))
                        seg2_fade = seg2.fade_in(int(entry_fade_in.get()))
                    else:
                        seg1_fade = seg1
                        seg2_fade = seg2
                    # Concatenate: End of seg1 + Transition Sound + Start of seg2
                    global_audio_merged = seg1_fade + sound_transition + seg2_fade
            
            # Update merged slider range
            merged_slider.config(to=len(global_audio_merged))
            merged_slider.set(0)

            # Bind slider release event for seeking
            merged_slider.bind("<ButtonRelease-1>", lambda e: on_slider_release(e, global_audio_merged, merged_slider, btn_play_merged, btn_stop_merged, btn_seg_merged))

            # Enable play and save buttons for merged audio
            btn_play_merged.config(state="normal")
            btn_save.config(state="normal")
            
            messagebox.showinfo("Success", "Tracks merged successfully!", parent=merger_win)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge tracks: {e}", parent=merger_win)

    sectionm = tk.LabelFrame(right_column, text="Merged Track", padx=10, pady=10)
    sectionm.pack(fill="x", padx=10, pady=5)

    # Row 1: Fade settings
    rowm1 = tk.Frame(sectionm)
    rowm1.pack(fill="x")

    tk.Label(rowm1, text="Fade Out(ms):").pack(side=tk.LEFT)
    entry_fade_out = tk.Entry(rowm1, width=5)
    entry_fade_out.insert(0, "2000") # default fade duration  
    entry_fade_out.pack(side=tk.LEFT)
    tk.Label(rowm1, text="Fade In(ms):").pack(side=tk.LEFT)
    entry_fade_in = tk.Entry(rowm1, width=5)
    entry_fade_in.insert(0, "2000") # default fade duration  
    entry_fade_in.pack(side=tk.LEFT)

    # Row 2: Info
    label_info = tk.Label(sectionm, text="Crossfade will happen using fade from 'Fade In'", fg="red")
    label_info.pack(fill="x", pady=5)

    # Row 3: Transition type
    tk.Label(sectionm, text="Transition Type:").pack(pady=5)
    combo_transition = ttk.Combobox(sectionm, values=["Crossfade", "Fade Out/In", "Insert Sound (Transition)"], state="readonly")
    combo_transition.current(0) 
    combo_transition.pack(pady=5)

    # Row 4: Controls
    # Set up browse buttons
    rowm4 = tk.Frame(sectionm)
    rowm4.pack(fill="x")
    tk.Button(rowm4, text="Merge Tracks", command=lambda: merge_tracks(entry_fade_out=entry_fade_out, entry_fade_in=entry_fade_in)).pack(pady=10)

    btn_play_merged = tk.Button(
        rowm4,
        text="▶ Play Merged",
        state="disabled",
        command=lambda: on_play_click(global_audio_merged, btn_play_merged, btn_stop_merged, btn_seg_merged, None, merged_slider)
    )
    btn_play_merged.pack(side=tk.LEFT)
    btn_stop_merged = tk.Button(rowm4, text="■ Stop", state="disabled", command=lambda: on_stop_click(btn_play_merged, btn_stop_merged, btn_seg_merged))
    btn_stop_merged.pack(side=tk.LEFT)

    # Segment preview controls for merged audio
    tk.Label(rowm4, text="Segment Start(ms):").pack(side=tk.LEFT)
    entry_seg_start = tk.Entry(rowm4, width=5)
    entry_seg_start.insert(0, "0")  
    entry_seg_start.pack(side=tk.LEFT)

    tk.Label(rowm4, text="Segment End(ms):").pack(side=tk.LEFT)
    entry_seg_end = tk.Entry(rowm4, width=5)
    entry_seg_end.insert(0, "0")  
    entry_seg_end.pack(side=tk.LEFT)

    btn_seg_merged = tk.Button(rowm4, text="▶ Play Merged Segment", state="disabled", command=lambda: play_segment_with_slider(
        global_audio_merged, 
        int(float(entry_seg_start.get() or 0) * 1000),
        int(float(entry_seg_end.get() or len(global_audio_merged) / 1000) * 1000), 
        btn_play_merged, 
        btn_stop_merged, 
        btn_seg_merged, 
        merged_slider
        )
    )
    btn_seg_merged.pack(side=tk.LEFT)  

    # Slider for merged audio position
    merged_slider = tk.Scale(sectionm, from_=0, to=1000, orient="horizontal", length=500, label="Merged Audio Position (ms)")
    merged_slider.pack(fill="x", pady=5)

    def save_merged(parent_win):
        """Saves the merged audio to a user-selected file location."""
        nonlocal global_audio_merged

        # Save the merged audio to a file
        if global_audio_merged:
            save_path = filedialog.asksaveasfilename(parent=parent_win, defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")])
            
            if save_path:
                try:
                    # Normalize the merged audio to prevent clipping
                    audio_to_save = global_audio_merged.normalize()
                    # force CBR and stereo + 44.1 kHz
                    audio_to_save.export( save_path, format="mp3", bitrate="192k", parameters=["-ac", "2", "-ar", "44100"] )
                    messagebox.showinfo("Saved", f"Merged audio saved to {save_path}", parent=parent_win)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}", parent=parent_win)

    # Save button for merged audio
    btn_save = tk.Button(right_column, text="💾 Save Merged", state="disabled", command=lambda: save_merged(merger_win))
    btn_save.pack(pady=5)

