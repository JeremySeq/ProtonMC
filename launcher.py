import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os

class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProtonMC Launcher")
        self.geometry("800x600")

        self.process = None

        self.start_button = tk.Button(self, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg="black", fg="white")
        self.output_area.pack(pady=10, padx=10, expand=True, fill="both")

    def start_server(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.output_area.insert(tk.INSERT, "Installing dependencies...\n")

        try:
            subprocess.check_call(["python", "-m", "pip", "install", "-r", "backend/requirements.txt"])
            self.output_area.insert(tk.INSERT, "Dependencies installed successfully.\n")
        except subprocess.CalledProcessError as e:
            self.output_area.insert(tk.INSERT, f"Error installing dependencies: {e}\n")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return

        self.output_area.insert(tk.INSERT, "Starting server...\n")

        self.process = subprocess.Popen(
            ["python", "backend/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )

        self.thread = threading.Thread(target=self.read_output)
        self.thread.daemon = True
        self.thread.start()

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.output_area.insert(tk.INSERT, "\nServer stopped.\n")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def read_output(self):
        for line in iter(self.process.stdout.readline, ''):
            self.output_area.insert(tk.INSERT, line)
            self.output_area.see(tk.END)
        self.process.stdout.close()
        self.process.wait()
        self.output_area.insert(tk.INSERT, "\nServer process finished.\n")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_closing(self):
        if self.process:
            self.stop_server()
        self.destroy()

if __name__ == "__main__":
    app = Launcher()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
