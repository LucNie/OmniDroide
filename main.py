import tkinter as tk
from tkinter import Canvas
import asyncio
import websockets
import cv2
from PIL import Image, ImageTk
import numpy as np

class RemoteControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Phone Control")

        self.canvas = Canvas(root, width=480, height=800, bg="black")
        self.canvas.pack()

        self.websocket = None
        self.running = True

        self.root.bind("<Key>", self.send_key)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Utilisation d'un thread pour gérer les tâches asynchrones
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.connect_to_server())
        self.loop.create_task(self.update_video())

    async def connect_to_server(self):
        try:
            self.websocket = await websockets.connect("ws://<PHONE_IP>:<PORT>")
            print("Connected to phone")
        except Exception as e:
            print(f"Connection error: {e}")

    async def update_video(self):
        while self.running:
            if self.websocket:
                try:
                    frame_data = await self.websocket.recv()
                    frame = np.frombuffer(frame_data, dtype=np.uint8)
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                    if frame is not None:
                        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        photo = ImageTk.PhotoImage(image=image)
                        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                        self.root.image = photo  # Prevent garbage collection
                except Exception as e:
                    print(f"Video update error: {e}")

    def send_key(self, event):
        if self.websocket:
            try:
                asyncio.create_task(self.websocket.send(event.keysym))  # Async task for sending keys
                print(f"Key sent: {event.keysym}")
            except Exception as e:
                print(f"Error sending key: {e}")

    def on_close(self):
        self.running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())  # Async task for closing connection
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteControlApp(root)
    
    # Pour que le programme fonctionne sous Tkinter, on lance la boucle d'événements de Tkinter
    # et la boucle d'événements asyncio en parallèle
    def run():
        asyncio.ensure_future(app.loop)
        root.mainloop()

    run()
