import tkinter as tk

class ComparisonTab:
    """Placeholder for comparison feature"""
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()
        
    def setup_ui(self):
        # Center frame
        center_frame = tk.Frame(self.frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(center_frame, text="🔍", font=("Arial", 48), 
                bg="#f0f0f0").pack(pady=10)
        tk.Label(center_frame, text="CHỨC NĂNG SO SÁNH", 
                font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(center_frame, 
                text="Tính năng so sánh các trường đại học\nđang được phát triển...", 
                font=("Arial", 12), bg="#f0f0f0", 
                justify="center").pack(pady=10)


