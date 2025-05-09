# Screen Clicker

A portable utility that monitors a selected screen area for a specific image, then performs automated mouse actions when the image is detected.

## Features

- Select a target area on your screen to monitor
- Choose where to click after the target is found
- Automatically right-clicks when the target is found
- Then automatically left-clicks at your chosen position
- Portable executable - no installation required

## How to Use

1. Launch the application
2. Click "Select Target Image" and draw a rectangle around the area you want to monitor
3. Click "Select Click Position" and click where you want the program to click after finding the target
4. Click "Start Monitoring" to begin watching for the target image
5. When the target is found, the program will automatically:
   - Right-click on the target area
   - Left-click at your chosen position
   - Stop monitoring

## Building from Source

If you want to build the executable yourself:

1. Install Python 3.7 or newer
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the build script:
   ```
   python build.py
   ```
4. Find the executable in the `dist` folder

## Technical Details

- Built with Python and Tkinter
- Uses PyAutoGUI for mouse control
- Uses PIL/Pillow for image processing
- Packaged with PyInstaller for portability
