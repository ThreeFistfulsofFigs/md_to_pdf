from gui import ConverterGUI
from converter import MarkdownConverter
from tkinter import filedialog, messagebox
import os
import threading
import webbrowser


class ConversionError(Exception):
    pass


class MarkdownConverterApp:
    def __init__(self):
        self.gui = ConverterGUI()
        self.converter = MarkdownConverter(self.gui)
        self.gui.convert_btn.config(command=self.select_files)

        # Add cancel button support
        if hasattr(self.gui, 'cancel_btn'):
            self.gui.cancel_btn.config(command=self.cancel_conversion)

        self.conversion_in_progress = False
        self.conversion_thread = None

    def cancel_conversion(self):
        """Cancel the ongoing conversion process."""
        if self.conversion_in_progress:
            self.conversion_in_progress = False
            self.gui.status_label.config(text="Conversion cancelled")
            self.gui.progress['value'] = 0
            self.gui.convert_btn.config(state='normal')
            if hasattr(self.gui, 'cancel_btn'):
                self.gui.cancel_btn.config(state='disabled')

            # Signal to converter to stop
            if hasattr(self.converter, 'cancel'):
                self.converter.cancel()

    def run_conversion(self, input_file, output_file):
        """Run the conversion process in a separate thread."""
        try:
            success = self.converter.convert(input_file, output_file)

            if not success:
                self.gui.status_label.config(text="Conversion failed or was cancelled")

        except Exception as e:
            # This will catch any exceptions that weren't handled in the converter
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            self.gui.status_label.config(text=error_msg)
            messagebox.showerror("Conversion Error", f"An unexpected error occurred: {str(e)}")

        finally:
            # Always make sure to reset the UI state
            self.conversion_in_progress = False
            self.gui.convert_btn.config(state='normal')
            if hasattr(self.gui, 'cancel_btn'):
                self.gui.cancel_btn.config(state='disabled')

    def select_files(self):
        """Handle file selection and start the conversion process."""
        if self.conversion_in_progress:
            return

        try:
            # Check for wkhtmltopdf before starting
            if not self.converter.wkhtmltopdf_path:
                if messagebox.askyesno("Dependency Missing",
                                       "wkhtmltopdf not found, which is required for PDF conversion.\n\n"
                                       "Would you like to open the download page?"):
                    webbrowser.open("https://wkhtmltopdf.org/downloads.html")
                return

            self.gui.status_label.config(text="Selecting files...")
            self.gui.progress['value'] = 0
            self.gui.root.update()

            input_file = filedialog.askopenfilename(
                title="Select Markdown file",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
            )

            if not input_file:
                self.gui.status_label.config(text="No input file selected")
                return

            # Validate file exists and is readable
            if not os.path.isfile(input_file):
                raise ConversionError("Input file does not exist")

            if not os.access(input_file, os.R_OK):
                raise ConversionError(f"Cannot read input file: {input_file}")

            # Default output filename based on input filename
            default_output = os.path.splitext(input_file)[0] + ".pdf"

            output_file = filedialog.asksaveasfilename(
                title="Save PDF as",
                defaultextension=".pdf",
                initialfile=os.path.basename(default_output),
                filetypes=[("PDF files", "*.pdf")]
            )

            if not output_file:
                self.gui.status_label.config(text="Conversion cancelled")
                return

            # Print paths for debugging
            print(f"Input file: {input_file}")
            print(f"Output file: {output_file}")

            if output_file:  # Ensure output_file is defined
                # Check if output directory is writable
                output_dir = os.path.dirname(os.path.abspath(output_file))
                if not os.path.exists(output_dir):
                    try:
                        os.makedirs(output_dir, exist_ok=True)  # Use exist_ok to avoid race condition
                    except Exception as e:
                        raise ConversionError(f"Cannot create output directory: {output_dir}. Error: {str(e)}")

                if not os.access(output_dir, os.W_OK):
                    raise ConversionError(f"Cannot write to output directory: {output_dir}")

            # Disable the convert button and enable the cancel button during conversion
            self.conversion_in_progress = True
            self.gui.convert_btn.config(state='disabled')
            if hasattr(self.gui, 'cancel_btn'):
                self.gui.cancel_btn.config(state='normal')

            # Start conversion in a separate thread to avoid freezing the UI
            self.conversion_thread = threading.Thread(
                target=self.run_conversion,
                args=(input_file, output_file)
            )
            self.conversion_thread.daemon = True
            self.conversion_thread.start()

        except ConversionError as e:
            messagebox.showerror("Conversion Error", str(e))
            self.gui.status_label.config(text="Conversion failed!")
            self.gui.progress['value'] = 0
            self.conversion_in_progress = False
            self.gui.convert_btn.config(state='normal')
            if hasattr(self.gui, 'cancel_btn'):
                self.gui.cancel_btn.config(state='disabled')

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.gui.status_label.config(text="Operation failed!")
            self.gui.progress['value'] = 0
            self.conversion_in_progress = False
            self.gui.convert_btn.config(state='normal')
            if hasattr(self.gui, 'cancel_btn'):
                self.gui.cancel_btn.config(state='disabled')

    def run(self):
        """Start the application."""
        # Check and notify about dependencies at startup
        if not self.converter.wkhtmltopdf_path:
            self.gui.status_label.config(
                text="Warning: wkhtmltopdf not found. PDF conversion may fail."
            )
            print("WARNING: wkhtmltopdf not found. You need to install it for this application to work.")
            print("Download it from: https://wkhtmltopdf.org/downloads.html")
        else:
            print(f"Using wkhtmltopdf: {self.converter.wkhtmltopdf_path}")

        self.gui.root.mainloop()


if __name__ == "__main__":
    app = MarkdownConverterApp()
    app.run()