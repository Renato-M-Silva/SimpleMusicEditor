import tkinter as tk
import Youtube2Mp3
import audio_merger

def main():
    root = tk.Tk()
    root.title("SME - Simple Music Editor")
    root.geometry("300x200")

    tk.Label(root, text="Main Menu", font=("Arial", 14)).pack(pady=10)
    
    # Buttons calling the modular functions
    tk.Button(root, text="YouTube Downloader", command=Youtube2Mp3.run_downloader).pack(pady=5)
    tk.Button(root, text="Audio Merger", command=audio_merger.run_merger).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()