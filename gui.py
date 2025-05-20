import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror


class ConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Markdown to PDF Converter")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure('TButton', padding=10)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text="Convert Markdown to PDF",
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(pady=10)

        self.convert_btn = ttk.Button(
            main_frame,
            text="Select and Convert",
        )
        self.convert_btn.pack(pady=20)

        # Add a cancel button
        self.cancel_btn = ttk.Button(
            main_frame,
            text="Cancel",
            state='disabled'
        )
        self.cancel_btn.pack(pady=5)

        self.progress = ttk.Progressbar(
            main_frame,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=10)

        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=('Helvetica', 10)
        )
        self.status_label.pack(pady=10)

    def show_status(self, message):
        """Update the status label with the given message."""
        self.status_label.config(text=message)
        self.root.update()

    def update_progress(self, value):
        """Update the progress bar with a value between 0-100."""
        self.progress['value'] = value
        self.root.update()