import pyautogui
import cv2
import numpy as np
import threading
import tkinter as tk
from tkinter import ttk
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import subprocess

# Configuration par défaut
resolution = (1280, 720)
fps = 30
bitrate = "2M"
encoder = "libx264"
streaming = False

app = FastAPI()

def generate_video():
    """ Capture l'écran et encode avec FFmpeg pour un streaming fluide compatible Chrome """
    global streaming

    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{resolution[0]}x{resolution[1]}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", encoder,
        "-preset", "ultrafast",  # Permet un encodage rapide
        "-b:v", bitrate,
        "-f", "mp4",
        "-movflags", "frag_keyframe+empty_moov",
        "pipe:1"
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)

    try:
        while streaming:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, resolution)

            process.stdin.write(frame.tobytes())

            # Lire les données encodées et les envoyer
            data = process.stdout.read(4096)
            if not data:
                break

            yield data

    except Exception as e:
        print(f"Erreur pendant le streaming : {e}")

    finally:
        streaming = False
        process.stdin.close()
        process.stdout.close()
        process.wait()

@app.get("/getVideo")
def get_video():
    """ Route API qui envoie un flux vidéo MP4 compatible avec un lecteur HTML5 """
    global streaming
    streaming = True
    return StreamingResponse(generate_video(), media_type="video/mp4")

def toggle_streaming():
    """ Démarre ou arrête le streaming vidéo """
    global streaming
    if not streaming:
        streaming = True
        toggle_button.config(text="Stop Streaming", bg="red")
        status_label.config(text="Streaming Live...", fg="red")
    else:
        streaming = False
        toggle_button.config(text="Start Streaming", bg="green")
        status_label.config(text="Not Streaming", fg="black")

def update_encoder():
    """ Met à jour l'encodeur sélectionné """
    global encoder
    encoder = encoder_var.get()

def update_bitrate():
    """ Met à jour le bitrate sélectionné """
    global bitrate
    bitrate = bitrate_entry.get() + "M"

# Interface Tkinter
root = tk.Tk()
root.title("Screen Streaming")
root.geometry("350x200")

toggle_button = tk.Button(root, text="Start Streaming", bg="green", fg="white", font=("Arial", 12), command=toggle_streaming)
toggle_button.pack(pady=10)

status_label = tk.Label(root, text="Not Streaming", font=("Arial", 10))
status_label.pack()

encoder_var = tk.StringVar(value="libx264")
encoder_label = tk.Label(root, text="Encoder:")
encoder_label.pack()
encoder_combo = ttk.Combobox(root, textvariable=encoder_var, values=["libx264", "libx265", "libsvtav1"])
encoder_combo.pack()
encoder_combo.bind("<<ComboboxSelected>>", lambda e: update_encoder())

bitrate_label = tk.Label(root, text="Bitrate (Mbps):")
bitrate_label.pack()
bitrate_entry = tk.Entry(root)
bitrate_entry.insert(0, "2")
bitrate_entry.pack()
bitrate_entry.bind("<Return>", lambda e: update_bitrate())

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

root.mainloop()
