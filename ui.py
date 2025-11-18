import tkinter as tk
from tkinter import scrolledtext
import threading

class ChatUI:
    def __init__(self, chat_engine):
        self.chat_engine = chat_engine

        self.root = tk.Tk()
        self.root.title("So sánh Đại học Quốc tế")
        self.root.geometry("1000x750")

        self.output = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state="disabled", font=("Consolas", 12)
        )
        self.output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry = tk.Entry(frame, font=("Consolas", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry.bind("<Return>", lambda e: self.send_message())

        send_btn = tk.Button(frame, text="Gửi", command=self.send_message, font=("Consolas", 12))
        send_btn.pack(side=tk.RIGHT)

    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.output.config(state="normal")
        self.output.insert(tk.END, f"Bạn: {user_text}\n")
        self.output.config(state="disabled")

        self.entry.delete(0, tk.END)

        threading.Thread(
            target=self.chat_engine.ask_stream,
            args=(user_text, self.output),
            daemon=True
        ).start()

    def run(self):
        self.root.mainloop()
