import g4f
import tkinter as tk

class ChatEngine:
    def __init__(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()

    def ask_stream(self, user_text, output_widget):
        try:
            self.chat_history.append({"role": "user", "content": user_text})

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history,
                stream=True,
            )

            output_widget.config(state="normal")
            output_widget.insert(tk.END, "Trợ lý: ")
            output_widget.config(state="disabled")

            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    full_reply += delta.content
                    output_widget.config(state="normal")
                    output_widget.insert(tk.END, delta.content)
                    output_widget.config(state="disabled")
                    output_widget.see(tk.END)

            self.chat_history.append({"role": "assistant", "content": full_reply})

            output_widget.config(state="normal")
            output_widget.insert(tk.END, "\n\n")
            output_widget.config(state="disabled")

        except Exception as e:
            output_widget.config(state="normal")
            output_widget.insert(tk.END, f"\n[Lỗi: {e}]\n\n")
            output_widget.config(state="disabled")
