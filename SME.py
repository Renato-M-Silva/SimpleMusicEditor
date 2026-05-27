import tkinter as tk
import Youtube2Mp3
import audio_merger
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

def open_downloader():
    # Toplevel creates a child window instead of a new app instance
    win = tk.Toplevel(root)
    Youtube2Mp3.run_downloader(win)

def open_merger():
    # Toplevel creates a child window instead of a new app instance
    win = tk.Toplevel(root)
    audio_merger.run_merger(win)

def main():
    global root
    root = tk.Tk()
    root.title("SME - Simple Music Editor")
    root.geometry("300x200")

    tk.Label(root, text="Main Menu", font=("Arial", 14)).pack(pady=10)
    
    tk.Button(root, text="YouTube Downloader", command=open_downloader).pack(pady=5)
    tk.Button(root, text="Audio Merger", command=open_merger).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()