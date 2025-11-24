import g4f

class ChatEngine:
    def __init__(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()

    def ask_stream(self, user_text, output_widget, on_response_start=None, status_callback=None):
        try:
            self.chat_history.append({"role": "user", "content": user_text})

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history,
                stream=True,
            )

            full_reply = ""
            first_chunk = True
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    # ✅ Gọi callback khi nhận chunk đầu tiên
                    if first_chunk and on_response_start:
                        on_response_start()
                        first_chunk = False
                    
                    full_reply += delta.content
                    output_widget.config(state="normal")
                    output_widget.insert("end", delta.content, "assistant_text")
                    output_widget.config(state="disabled")
                    output_widget.see("end")

            self.chat_history.append({"role": "assistant", "content": full_reply})

            output_widget.config(state="normal")
            output_widget.insert("end", "\n\n")
            output_widget.config(state="disabled")
            
            if status_callback:
                status_callback(False)

        except Exception as e:
            output_widget.config(state="normal")
            output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
            output_widget.config(state="disabled")
            if status_callback:
                status_callback(False)

    def clear_history(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]