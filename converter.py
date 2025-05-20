import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror, showinfo
import markdown2
import pdfkit
import os
import sys
import subprocess
import tempfile
from pathlib import Path


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
        self.convert_btn.config(command=self.on_convert_click)

        # Add a cancel button for better user control
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

    def on_convert_click(self):
        # This is just a placeholder - it will be overridden in the main app
        pass

    def update_progress(self, value):
        """Update the progress bar with a value between 0-100."""
        self.progress['value'] = value
        self.root.update()


class MarkdownConverter:
    def __init__(self, gui):
        self.gui = gui
        self.cancelled = False
        # Check for wkhtmltopdf installation
        self.wkhtmltopdf_path = self._find_wkhtmltopdf()
        print(f"Using wkhtmltopdf path: {self.wkhtmltopdf_path}")

    def _find_wkhtmltopdf(self):
        """Try to find the wkhtmltopdf executable."""
        # Try to get path from pdfkit config
        try:
            return pdfkit.configuration().wkhtmltopdf
        except Exception as e:
            print(f"Error getting wkhtmltopdf from pdfkit config: {str(e)}")
            pass

        # Common installation paths
        possible_paths = [
            # Windows
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
            # macOS (Homebrew)
            '/usr/local/bin/wkhtmltopdf',
            # Linux
            '/usr/bin/wkhtmltopdf',
            '/usr/local/bin/wkhtmltopdf',
        ]

        for path in possible_paths:
            if os.path.isfile(path):
                print(f"Found wkhtmltopdf at: {path}")
                return path

        # Last resort: check if it's in PATH
        try:
            if sys.platform == 'win32':
                # Windows
                result = subprocess.run(['where', 'wkhtmltopdf'], check=True, stdout=subprocess.PIPE)
                path = result.stdout.decode('utf-8').strip().split('\n')[0]
                print(f"Found wkhtmltopdf in PATH: {path}")
                return path
            else:
                # Unix-like
                result = subprocess.run(['which', 'wkhtmltopdf'], check=True, stdout=subprocess.PIPE)
                path = result.stdout.decode('utf-8').strip()
                print(f"Found wkhtmltopdf in PATH: {path}")
                return path
        except Exception as e:
            print(f"Error finding wkhtmltopdf in PATH: {str(e)}")
            return None  # Not found

    def cancel(self):
        """Cancel the current conversion process."""
        self.cancelled = True

    def check_dependencies(self):
        """Check if all required dependencies are installed."""
        if not self.wkhtmltopdf_path:
            raise RuntimeError(
                "wkhtmltopdf not found. Please install it from https://wkhtmltopdf.org/downloads.html"
            )
        return True

    def convert(self, input_file, output_file):
        """Convert markdown to PDF with detailed progress updates."""
        temp_html_path = None
        try:
            self.cancelled = False

            # Check dependencies first
            self.gui.show_status("Checking dependencies...")
            self.gui.update_progress(10)
            self.check_dependencies()

            if self.cancelled:
                return False

            # Step 1: Read the markdown file
            self.gui.show_status("Reading markdown file...")
            self.gui.update_progress(20)
            content = self.read_file(input_file)

            if self.cancelled:
                return False

            # Step 2: Convert markdown to HTML
            self.gui.show_status("Converting markdown to HTML...")
            self.gui.update_progress(40)
            html = markdown2.markdown(content, extras=['tables', 'code-friendly'])

            # Add basic styling to HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{Path(input_file).stem}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2em; }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ background-color: #f4f4f4; border-radius: 3px; padding: 2px 5px; }}
                    pre {{ background-color: #f4f4f4; border-radius: 5px; padding: 10px; overflow-x: auto; }}
                    blockquote {{ border-left: 5px solid #ddd; padding-left: 15px; color: #555; }}
                    img {{ max-width: 100%; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """

            if self.cancelled:
                return False

            # Step 3: Create temporary HTML file
            # Use tempfile module to create a temporary file with appropriate suffix
            fd, temp_html_path = tempfile.mkstemp(suffix=".html")
            os.close(fd)

            self.gui.show_status(f"Creating HTML file at {temp_html_path}...")
            self.gui.update_progress(60)

            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html)

            if self.cancelled:
                # Clean up temp file
                if temp_html_path and os.path.exists(temp_html_path):
                    try:
                        os.remove(temp_html_path)
                    except:
                        pass
                return False

            # Step 4: Convert HTML to PDF
            self.gui.show_status("Converting HTML to PDF...")
            self.gui.update_progress(80)

            # Configure pdfkit
            options = {
                'quiet': '',
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                # Remove verbose option as it's not supported in all versions
            }

            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_file))
            os.makedirs(output_dir, exist_ok=True)

            print(f"Converting {temp_html_path} to {output_file}")

            # Create PDF configuration
            if self.wkhtmltopdf_path and self.wkhtmltopdf_path != 'wkhtmltopdf':
                config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
                print(f"Using wkhtmltopdf path: {self.wkhtmltopdf_path}")
                pdfkit.from_file(temp_html_path, output_file, options=options, configuration=config)
            else:
                print("Using default wkhtmltopdf from PATH")
                pdfkit.from_file(temp_html_path, output_file, options=options)

            # Clean up temp file
            if temp_html_path and os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                except Exception as e:
                    print(f"Error removing temp file: {str(e)}")

            # Check if the PDF was actually created
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise RuntimeError("PDF file was not created successfully")

            self.gui.show_status("Conversion completed successfully!")
            self.gui.update_progress(100)

            # Show success message with file path
            showinfo("Conversion Complete", f"PDF saved to:\n{output_file}")
            return True

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            self.gui.show_status(error_msg)
            self.gui.update_progress(0)
            showerror("Conversion Error", f"Failed to convert: {str(e)}")
            return False
        finally:
            # Make sure to clean up temp file
            if temp_html_path and os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                except:
                    pass

    def read_file(self, input_file):
        """Read markdown content from a file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(input_file, 'r', encoding='latin-1') as file:
                return file.read()