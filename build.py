import os
import subprocess
import sys

def build_executable():
    print("Building Screen Clicker executable...")
    
    # Command to build the executable
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--icon=icon.ico",
        "--name=AdvancedScreenClicker",
        "--add-data=icon.ico;.",
        "--hidden-import=pytesseract",
        "advanced_screen_clicker.py"
    ]
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"Executable created at: {os.path.abspath('dist/AdvancedScreenClicker.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()
