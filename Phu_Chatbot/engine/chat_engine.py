import g4f

class ChatEngine:
    """Engine để giao tiếp với AI model"""
    
    def __init__(self, system_prompt):
        """
        Khởi tạo ChatEngine
        
        Args:
            system_prompt: System prompt cho AI
        """
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()

    def ask_stream(self, user_text, output_widget, status_callback=None):
        """
        Gửi tin nhắn và nhận phản hồi dạng stream
        
        Args:
            user_text: Nội dung tin nhắn từ user
            output_widget: Widget để hiển thị kết quả
            status_callback: Callback để cập nhật trạng thái
        """
        try:
            self.chat_history.append({"role": "user", "content": user_text})

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history,
                stream=True,
            )

            output_widget.config(state="normal")
            output_widget.insert("end", "🤖 Trợ lý: ", "assistant_label")
            output_widget.config(state="disabled")

            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
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
        """
        Reset lịch sử chat
        
        Args:
            system_prompt: System prompt mới
        """
        self.chat_history = [{"role": "system", "content": system_prompt}]