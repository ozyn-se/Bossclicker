@echo off
echo Building Screen Clicker Executable...
echo.
echo This will install required dependencies and create a standalone executable.
echo.
echo Please ensure you have Python installed before running this script.
echo.
pause

:: Install required packages
pip install -r requirements.txt

:: Build the executable
pyinstaller --onefile --windowed --icon=icon.ico --name=ScreenClicker screen_clicker.py

echo.
echo Build complete! You can find the executable in the "dist" folder.
pause
