import time


def check_and_install_dependencies():
    """Check if required dependencies are installed and install them if needed."""
    required_packages = ['markdown2', 'pdfkit']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is already installed")
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("\nMissing dependencies detected. Installing required packages...")
        for package in missing_packages:
            try:
                import pip
                pip.main(['install', package])
                print(f"✓ Successfully installed {package}")
            except Exception as e:
                print(f"✗ Failed to install {package}: {e}")
                return False

        print("\nAll dependencies installed successfully!")
        return True
    else:
        print("All dependencies are already installed.")
        return True


# Run the main application
try:
    print("Checking dependencies...")
    if check_and_install_dependencies():
        print("\nStarting Markdown to PDF Converter...\n")
        import main

        app = main.MarkdownConverterApp()
        app.run()
    else:
        print("\nFailed to install required dependencies.")
        print("Please install the missing packages manually and try again.")
        time.sleep(5)
except Exception as e:
    import traceback

    print(f"\nError launching application: {e}")
    traceback.print_exc()
    # Keep the window open if there's an error
    input("\nPress Enter to close this window...")