import sys
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, Label, Button, Frame, Scale, HORIZONTAL
import pyautogui
import numpy as np
from PIL import Image, ImageTk, ImageGrab
from skimage.metrics import structural_similarity as ssim
import cv2
import json
import pickle
import base64
from io import BytesIO
import pytesseract

# Set path to tesseract executable if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'path_to_tesseract_executable'

class AdvancedScreenClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Screen Clicker")
        self.root.geometry("500x550")  # Increased height for new UI elements
        self.root.resizable(False, False)
        
        # Settings file path
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "advanced_settings.json")
        
        # Initialize variables
        self.image1 = None
        self.image1_position = None
        self.image2 = None
        self.image2_position = None
        self.image3 = None  # Added new image3
        self.image3_position = None  # Added new image3 position
        self.position3 = None
        self.monitoring = False
        self.monitor_thread = None
        self.loop_delay = 5.0  # Default 5 seconds
        self.click_delay = 0.5  # Default 0.5 seconds
        
        # Load settings if they exist
        self.load_settings()
        
        # Create UI
        self.create_widgets()
        
        # Set up auto-save on exit
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
    def save_settings(self):
        """Save current settings to a file"""
        try:
            settings = {}
            
            # Save image1 settings
            if self.image1_position:
                settings["image1_position"] = list(self.image1_position)
            
            # Save image2 settings
            if self.image2_position:
                settings["image2_position"] = list(self.image2_position)
            
            # Save image3 settings
            if self.image3_position:
                settings["image3_position"] = list(self.image3_position)
            
            # Save position3
            if self.position3:
                settings["position3"] = list(self.position3)
            
            # Save delay settings
            settings["loop_delay"] = self.loop_delay
            settings["click_delay"] = self.click_delay
            
            # Save images if they exist
            if self.image1:
                buffered = BytesIO()
                self.image1.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                settings["image1"] = img_str
            
            if self.image2:
                buffered = BytesIO()
                self.image2.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                settings["image2"] = img_str
                
            if self.image3:
                buffered = BytesIO()
                self.image3.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                settings["image3"] = img_str
            
            # Write settings to file
            with open(self.settings_file, "w") as f:
                json.dump(settings, f)
                
            print(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False
    
    def load_settings(self):
        """Load settings from file if it exists"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                
                # Load image1 settings
                if "image1_position" in settings:
                    self.image1_position = tuple(settings["image1_position"])
                
                # Load image2 settings
                if "image2_position" in settings:
                    self.image2_position = tuple(settings["image2_position"])
                    
                # Load image3 settings
                if "image3_position" in settings:
                    self.image3_position = tuple(settings["image3_position"])
                
                # Load position3
                if "position3" in settings:
                    self.position3 = tuple(settings["position3"])
                
                # Load delay settings
                if "loop_delay" in settings:
                    self.loop_delay = settings["loop_delay"]
                
                if "click_delay" in settings:
                    self.click_delay = settings["click_delay"]
                
                # Load image1 if it exists
                if "image1" in settings:
                    img_data = base64.b64decode(settings["image1"])
                    self.image1 = Image.open(BytesIO(img_data))
                
                # Load image2 if it exists
                if "image2" in settings:
                    img_data = base64.b64decode(settings["image2"])
                    self.image2 = Image.open(BytesIO(img_data))
                    
                # Load image3 if it exists
                if "image3" in settings:
                    img_data = base64.b64decode(settings["image3"])
                    self.image3 = Image.open(BytesIO(img_data))
                
                print(f"Settings loaded from {self.settings_file}")
                return True
            return False
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            return False
            
    def create_widgets(self):
        # Main frame
        main_frame = Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions for Image 1
        Label(main_frame, text="1. Select Image 1 for OCR and left-click", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Button to select first target image
        self.image1_btn = Button(main_frame, text="Select Image 1", command=self.select_image1)
        self.image1_btn.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Display selected image 1 position
        self.image1_pos_label = Label(main_frame, text="Not selected")
        self.image1_pos_label.grid(row=1, column=1, sticky="w", padx=5)
        
        # Instructions for Image 2
        Label(main_frame, text="2. Select Image 2 for left-click", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        # Button to select second target image
        self.image2_btn = Button(main_frame, text="Select Image 2", command=self.select_image2)
        self.image2_btn.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        # Display selected image 2 position
        self.image2_pos_label = Label(main_frame, text="Not selected")
        self.image2_pos_label.grid(row=3, column=1, sticky="w", padx=5)
        
        # Instructions for Image 3
        Label(main_frame, text="3. Select Image 3 for left-click", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 5))
        
        # Button to select third target image
        self.image3_btn = Button(main_frame, text="Select Image 3", command=self.select_image3)
        self.image3_btn.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        
        # Display selected image 3 position
        self.image3_pos_label = Label(main_frame, text="Not selected")
        self.image3_pos_label.grid(row=5, column=1, sticky="w", padx=5)
        
        # Instructions for Position 3
        Label(main_frame, text="4. Select Position 3 for final left-click", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", pady=(10, 5))
        
        # Button to select final position
        self.pos3_btn = Button(main_frame, text="Select Position 3", command=self.select_position3)
        self.pos3_btn.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        
        # Display selected final position
        self.pos3_label = Label(main_frame, text="Not selected")
        self.pos3_label.grid(row=7, column=1, sticky="w", padx=5)
        
        # Loop Delay Slider
        Label(main_frame, text="Loop Delay (seconds):", font=("Arial", 10)).grid(row=8, column=0, sticky="w", pady=(15, 0))
        self.loop_delay_slider = Scale(main_frame, from_=1, to=60, orient=HORIZONTAL, length=200,
                                      command=self.update_loop_delay)
        self.loop_delay_slider.set(self.loop_delay)
        self.loop_delay_slider.grid(row=9, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))
        
        # Click Delay Slider
        Label(main_frame, text="Click Delay (seconds):", font=("Arial", 10)).grid(row=10, column=0, sticky="w", pady=(5, 0))
        self.click_delay_slider = Scale(main_frame, from_=0.01, to=5.0, resolution=0.01, orient=HORIZONTAL, length=200,
                                       command=self.update_click_delay)
        self.click_delay_slider.set(self.click_delay)
        self.click_delay_slider.grid(row=11, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))
        
        # Control buttons frame
        control_frame = Frame(main_frame)
        control_frame.grid(row=12, column=0, columnspan=2, pady=10, sticky="w")
        
        # Start/Stop button
        self.start_btn = Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Save settings button
        self.save_btn = Button(control_frame, text="Save Settings", command=self.save_settings_with_feedback)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings status label
        self.settings_label = Label(main_frame, text="No saved settings found", fg="gray")
        self.settings_label.grid(row=13, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Status label
        self.status_label = Label(main_frame, text="Ready", fg="blue")
        self.status_label.grid(row=14, column=0, columnspan=2, sticky="w", pady=5)
    
    def update_loop_delay(self, value):
        self.loop_delay = float(value)
        print(f"Loop delay updated to {self.loop_delay} seconds")
    
    def update_click_delay(self, value):
        self.click_delay = float(value)
        print(f"Click delay updated to {self.click_delay} seconds")
    
    def select_image1(self):
        """Capture a region of the screen as the first target image"""
        self.root.iconify()
        self.status_label.config(text="Selecting Image 1...")
        
        # Create a temporary transparent window to capture screen region
        capture_window = tk.Toplevel(self.root)
        capture_window.attributes("-alpha", 0.3)  # Semi-transparent
        capture_window.attributes("-fullscreen", True)
        capture_window.attributes("-topmost", True)
        
        # Draw canvas for selection
        canvas = tk.Canvas(capture_window, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = tk.Label(capture_window, text="Click and drag to select the image area", 
                                     font=("Arial", 24), bg="white")
        instruction_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Variables to store selection coordinates
        start_x = start_y = end_x = end_y = 0
        rect_id = None
        
        def on_press(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)
        
        def on_drag(event):
            nonlocal rect_id, end_x, end_y
            end_x, end_y = event.x, event.y
            canvas.coords(rect_id, start_x, start_y, end_x, end_y)
        
        def on_release(event):
            nonlocal start_x, start_y, end_x, end_y
            # Ensure start coordinates are smaller than end coordinates
            if start_x > end_x:
                start_x, end_x = end_x, start_x
            if start_y > end_y:
                start_y, end_y = end_y, start_y
                
            # Capture the selected region
            capture_window.destroy()
            self.root.after(300, lambda: self.capture_image1(start_x, start_y, end_x, end_y))
        
        # Bind mouse events
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Cancel button
        def cancel():
            capture_window.destroy()
            self.root.deiconify()
            self.status_label.config(text="Image selection cancelled")
        
        cancel_btn = tk.Button(capture_window, text="Cancel", command=cancel)
        cancel_btn.place(relx=0.5, rely=0.9, anchor="center")
    
    def capture_image1(self, start_x, start_y, end_x, end_y):
        """Capture the selected region as image 1"""
        try:
            # Capture the screen region
            screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
            self.image1 = screenshot
            self.image1_position = (start_x, start_y, end_x, end_y)
            
            # Display a thumbnail of the captured image
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((100, 100))
            self.image1_thumbnail = ImageTk.PhotoImage(thumbnail)
            
            # Create a small display for the thumbnail if it doesn't exist
            if not hasattr(self, 'image1_display'):
                self.image1_display = Label(self.root)
                self.image1_display.place(x=350, y=50)  # Moved to the right side of the window
                
            self.image1_display.config(image=self.image1_thumbnail)
            
            # Update position label
            self.image1_pos_label.config(text=f"({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            # Try to extract text with OCR for monitoring
            try:
                self.image1_text = pytesseract.image_to_string(self.image1).strip()
                print(f"OCR Text from Image 1: {self.image1_text}")
                if not self.image1_text:
                    self.status_label.config(text="No text detected in Image 1! Will use image comparison instead.")
            except Exception as e:
                print(f"OCR error: {str(e)}")
                self.image1_text = None
                self.status_label.config(text="OCR failed! Will use image comparison instead.")
            
            self.status_label.config(text="Image 1 captured successfully!")
            
        except Exception as e:
            self.status_label.config(text=f"Error capturing image: {str(e)}")
        finally:
            self.root.deiconify()
    
    def select_image2(self):
        """Capture a region of the screen as the second target image"""
        self.root.iconify()
        self.status_label.config(text="Selecting Image 2...")
        
        # Create a temporary transparent window to capture screen region
        capture_window = tk.Toplevel(self.root)
        capture_window.attributes("-alpha", 0.3)  # Semi-transparent
        capture_window.attributes("-fullscreen", True)
        capture_window.attributes("-topmost", True)
        
        # Draw canvas for selection
        canvas = tk.Canvas(capture_window, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = tk.Label(capture_window, text="Click and drag to select the image area", 
                                     font=("Arial", 24), bg="white")
        instruction_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Variables to store selection coordinates
        start_x = start_y = end_x = end_y = 0
        rect_id = None
        
        def on_press(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)
        
        def on_drag(event):
            nonlocal rect_id, end_x, end_y
            end_x, end_y = event.x, event.y
            canvas.coords(rect_id, start_x, start_y, end_x, end_y)
        
        def on_release(event):
            nonlocal start_x, start_y, end_x, end_y
            # Ensure start coordinates are smaller than end coordinates
            if start_x > end_x:
                start_x, end_x = end_x, start_x
            if start_y > end_y:
                start_y, end_y = end_y, start_y
                
            # Capture the selected region
            capture_window.destroy()
            self.root.after(300, lambda: self.capture_image2(start_x, start_y, end_x, end_y))
        
        # Bind mouse events
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Cancel button
        def cancel():
            capture_window.destroy()
            self.root.deiconify()
            self.status_label.config(text="Image selection cancelled")
        
        cancel_btn = tk.Button(capture_window, text="Cancel", command=cancel)
        cancel_btn.place(relx=0.5, rely=0.9, anchor="center")
    
    def capture_image2(self, start_x, start_y, end_x, end_y):
        """Capture the selected region as image 2"""
        try:
            # Capture the screen region
            screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
            self.image2 = screenshot
            self.image2_position = (start_x, start_y, end_x, end_y)
            
            # Display a thumbnail of the captured image
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((100, 100))
            self.image2_thumbnail = ImageTk.PhotoImage(thumbnail)
            
            # Create a small display for the thumbnail if it doesn't exist
            if not hasattr(self, 'image2_display'):
                self.image2_display = Label(self.root)
                self.image2_display.place(x=350, y=160)  # Moved to the right side of the window below image1
                
            self.image2_display.config(image=self.image2_thumbnail)
            
            # Update position label
            self.image2_pos_label.config(text=f"({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            # Try to extract text with OCR for reference
            try:
                image2_text = pytesseract.image_to_string(self.image2).strip()
                print(f"OCR Text from Image 2: {image2_text}")
            except Exception as e:
                print(f"OCR error on Image 2: {str(e)}")
            
            self.status_label.config(text="Image 2 captured successfully!")
            
        except Exception as e:
            self.status_label.config(text=f"Error capturing image: {str(e)}")
        finally:
            self.root.deiconify()
    
    def select_image3(self):
        """Capture a region of the screen as the third target image"""
        self.root.iconify()
        self.status_label.config(text="Selecting Image 3...")
        
        # Create a temporary transparent window to capture screen region
        capture_window = tk.Toplevel(self.root)
        capture_window.attributes("-alpha", 0.3)  # Semi-transparent
        capture_window.attributes("-fullscreen", True)
        capture_window.attributes("-topmost", True)
        
        # Draw canvas for selection
        canvas = tk.Canvas(capture_window, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = tk.Label(capture_window, text="Click and drag to select the image area", 
                                     font=("Arial", 24), bg="white")
        instruction_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Variables to store selection coordinates
        start_x = start_y = end_x = end_y = 0
        rect_id = None
        
        def on_press(event):
            nonlocal start_x, start_y, rect_id
            start_x, start_y = event.x, event.y
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)
        
        def on_drag(event):
            nonlocal rect_id, end_x, end_y
            end_x, end_y = event.x, event.y
            canvas.coords(rect_id, start_x, start_y, end_x, end_y)
        
        def on_release(event):
            nonlocal start_x, start_y, end_x, end_y
            # Ensure start coordinates are smaller than end coordinates
            if start_x > end_x:
                start_x, end_x = end_x, start_x
            if start_y > end_y:
                start_y, end_y = end_y, start_y
                
            # Capture the selected region
            capture_window.destroy()
            self.root.after(300, lambda: self.capture_image3(start_x, start_y, end_x, end_y))
        
        # Bind mouse events
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Cancel button
        def cancel():
            capture_window.destroy()
            self.root.deiconify()
            self.status_label.config(text="Image selection cancelled")
        
        cancel_btn = tk.Button(capture_window, text="Cancel", command=cancel)
        cancel_btn.place(relx=0.5, rely=0.9, anchor="center")
    
    def capture_image3(self, start_x, start_y, end_x, end_y):
        """Capture the selected region as image 3"""
        try:
            # Capture the screen region
            screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x, end_y))
            self.image3 = screenshot
            self.image3_position = (start_x, start_y, end_x, end_y)
            
            # Display a thumbnail of the captured image
            thumbnail = screenshot.copy()
            thumbnail.thumbnail((100, 100))
            self.image3_thumbnail = ImageTk.PhotoImage(thumbnail)
            
            # Create a small display for the thumbnail if it doesn't exist
            if not hasattr(self, 'image3_display'):
                self.image3_display = Label(self.root)
                self.image3_display.place(x=350, y=270)  # Moved to the right side of the window below image2
                
            self.image3_display.config(image=self.image3_thumbnail)
            
            # Update position label
            self.image3_pos_label.config(text=f"({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            # Try to extract text with OCR for reference
            try:
                image3_text = pytesseract.image_to_string(self.image3).strip()
                print(f"OCR Text from Image 3: {image3_text}")
            except Exception as e:
                print(f"OCR error on Image 3: {str(e)}")
            
            self.status_label.config(text="Image 3 captured successfully!")
            
        except Exception as e:
            self.status_label.config(text=f"Error capturing image: {str(e)}")
        finally:
            self.root.deiconify()
    
    def select_position3(self):
        """Select the final position for left-clicking"""
        self.root.iconify()
        self.status_label.config(text="Select Position 3...")
        
        # Create a transparent fullscreen window
        select_window = tk.Toplevel(self.root)
        select_window.attributes("-alpha", 0.3)
        select_window.attributes("-fullscreen", True)
        select_window.attributes("-topmost", True)
        
        # Add canvas for crosshair
        canvas = tk.Canvas(select_window, cursor="cross")
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instruction_label = tk.Label(select_window, 
                                    text="Click on the position for the final click", 
                                    font=("Arial", 24), bg="white")
        instruction_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Current mouse position display
        pos_label = tk.Label(select_window, text="Position: (0, 0)", 
                           font=("Arial", 14), bg="white")
        pos_label.place(relx=0.5, rely=0.9, anchor="center")
        
        # Crosshair
        h_line = canvas.create_line(0, 0, 0, 0, fill="red", width=1)
        v_line = canvas.create_line(0, 0, 0, 0, fill="red", width=1)
        
        def on_mouse_move(event):
            # Update crosshair position
            canvas.coords(h_line, 0, event.y, select_window.winfo_width(), event.y)
            canvas.coords(v_line, event.x, 0, event.x, select_window.winfo_height())
            
            # Update position label
            pos_label.config(text=f"Position: ({event.x}, {event.y})")
        
        def on_click(event):
            self.position3 = (event.x, event.y)
            select_window.destroy()
            self.root.deiconify()
            
            # Update position label in main window
            self.pos3_label.config(text=f"({event.x}, {event.y})")
            self.status_label.config(text="Position 3 selected!")
        
        # Bind events
        canvas.bind("<Motion>", on_mouse_move)
        canvas.bind("<Button-1>", on_click)
        
        # Cancel button
        def cancel():
            select_window.destroy()
            self.root.deiconify()
            self.status_label.config(text="Position selection cancelled")
        
        cancel_btn = tk.Button(select_window, text="Cancel", command=cancel)
        cancel_btn.place(relx=0.5, rely=0.95, anchor="center")
    
    def toggle_monitoring(self):
        """Start or stop the continuous monitoring process"""
        if self.monitoring:
            # Stop monitoring
            self.monitoring = False
            self.start_btn.config(text="Start Monitoring")
            self.image1_btn.config(state=tk.NORMAL)
            self.image2_btn.config(state=tk.NORMAL)
            self.image3_btn.config(state=tk.NORMAL)  # Enable image3 button
            self.pos3_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Monitoring stopped")
        else:
            # Check if all required selections have been made
            missing = []
            if not self.image1:
                missing.append("Image 1")
            if not self.image2:
                missing.append("Image 2")
            if not self.image3:
                missing.append("Image 3")  # Check for image3
            if not self.position3:
                missing.append("Position 3")
            
            if missing:
                messagebox.showwarning("Missing Selections", 
                                     f"Please select the following before starting: {', '.join(missing)}")
                return
            
            # Start monitoring
            self.monitoring = True
            self.start_btn.config(text="Stop Monitoring")
            self.image1_btn.config(state=tk.DISABLED)
            self.image2_btn.config(state=tk.DISABLED)
            self.image3_btn.config(state=tk.DISABLED)  # Disable image3 button
            self.pos3_btn.config(state=tk.DISABLED)
            
            # Start the monitoring thread
            self.status_label.config(text="Starting monitoring...")
            self.monitor_thread = threading.Thread(target=self.monitor_screen, daemon=True)
            self.monitor_thread.start()
    
    def monitor_screen(self):
        """Monitor the screen for the target images in sequence"""
        state = "waiting_for_image1"  # Initial state
        
        while self.monitoring:
            try:
                if state == "waiting_for_image1":
                    # Update status via the main thread
                    self.root.after(0, lambda: self.status_label.config(text="Looking for Image 1..."))
                    
                    # Check if Image 1 appears
                    found_image1 = self.check_for_image1()
                    
                    if found_image1:
                        # Found Image 1, perform click and move to next state
                        self.root.after(0, lambda: self.status_label.config(text="Image 1 found! Clicking..."))
                        self.click_image1()
                        state = "waiting_for_image2"
                
                elif state == "waiting_for_image2":
                    # Update status via the main thread
                    self.root.after(0, lambda: self.status_label.config(text="Looking for Image 2..."))
                    
                    # Check if Image 2 appears
                    found_image2 = self.check_for_image2()
                    
                    if found_image2:
                        # Found Image 2, perform click and move to next state
                        self.root.after(0, lambda: self.status_label.config(text="Image 2 found! Clicking..."))
                        self.click_image2()
                        state = "waiting_for_image3"
                
                elif state == "waiting_for_image3":
                    # Update status via the main thread
                    self.root.after(0, lambda: self.status_label.config(text="Looking for Image 3..."))
                    
                    # Check if Image 3 appears
                    found_image3 = self.check_for_image3()
                    
                    if found_image3:
                        # Found Image 3, perform click and move to next state
                        self.root.after(0, lambda: self.status_label.config(text="Image 3 found! Clicking..."))
                        self.click_image3()
                        state = "clicking_position3"
                
                elif state == "clicking_position3":
                    # Update status via the main thread
                    self.root.after(0, lambda: self.status_label.config(text="Clicking Position 3..."))
                    
                    # Perform the final click
                    self.click_position3()
                    
                    # Wait for the specified loop delay before starting over
                    timestamp = time.strftime("%H:%M:%S")
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Completed full sequence at {timestamp}. Waiting {self.loop_delay}s before next check..."))
                    
                    # Reset to the initial state
                    state = "waiting_for_image1"
                    
                    # Wait for loop delay before starting over
                    time.sleep(self.loop_delay)
                
            except Exception as e:
                error_msg = f"Error during monitoring: {str(e)}"
                print(error_msg)
                self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
                time.sleep(self.loop_delay)  # Wait before trying again
        
        # Clean up when stopped
        self.root.after(0, self.reset_ui)
    
    def check_for_image1(self):
        """Check if Image 1 appears at its position"""
        if not self.image1 or not self.image1_position:
            return False
        
        try:
            # Capture the current screen at the image1 position
            x1, y1, x2, y2 = self.image1_position
            current_screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Try OCR first if we have image1_text
            if hasattr(self, 'image1_text') and self.image1_text:
                try:
                    current_text = pytesseract.image_to_string(current_screenshot).strip()
                    print(f"Current OCR text: {current_text}")
                    print(f"Looking for OCR text: {self.image1_text}")
                    
                    # Check if the OCR text matches (allowing for partial matches)
                    if self.image1_text in current_text or current_text in self.image1_text:
                        print("OCR text match found!")
                        return True
                except Exception as e:
                    print(f"OCR comparison error: {str(e)}")
            
            # Fall back to image comparison
            return self.compare_images(self.image1, current_screenshot)
            
        except Exception as e:
            print(f"Error checking for image1: {str(e)}")
            return False
    
    def check_for_image2(self):
        """Check if Image 2 appears at its position"""
        if not self.image2 or not self.image2_position:
            return False
        
        try:
            # Capture the current screen at the image2 position
            x1, y1, x2, y2 = self.image2_position
            current_screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Compare images
            return self.compare_images(self.image2, current_screenshot)
            
        except Exception as e:
            print(f"Error checking for image2: {str(e)}")
            return False
    
    def check_for_image3(self):
        """Check if Image 3 appears at its position"""
        if not self.image3 or not self.image3_position:
            return False
        
        try:
            # Capture the current screen at the image3 position
            x1, y1, x2, y2 = self.image3_position
            current_screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Compare images
            return self.compare_images(self.image3, current_screenshot)
            
        except Exception as e:
            print(f"Error checking for image3: {str(e)}")
            return False
    
    def click_image1(self):
        """Click in the center of Image 1"""
        if not self.image1_position:
            return
        
        try:
            # Calculate center of image1
            x1, y1, x2, y2 = self.image1_position
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Move mouse and left-click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.leftClick()
            
            # Wait for the specified click delay
            time.sleep(self.click_delay)
            
        except Exception as e:
            print(f"Error clicking image1: {str(e)}")
    
    def click_image2(self):
        """Click in the center of Image 2"""
        if not self.image2_position:
            return
        
        try:
            # Calculate center of image2
            x1, y1, x2, y2 = self.image2_position
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Move mouse and left-click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.leftClick()
            
            # Wait for the specified click delay
            time.sleep(self.click_delay)
            
        except Exception as e:
            print(f"Error clicking image2: {str(e)}")
    
    def click_image3(self):
        """Click in the center of Image 3"""
        if not self.image3_position:
            return
        
        try:
            # Calculate center of image3
            x1, y1, x2, y2 = self.image3_position
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # Move mouse and left-click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.leftClick()
            
            # Wait for the specified click delay
            time.sleep(self.click_delay)
            
        except Exception as e:
            print(f"Error clicking image3: {str(e)}")
    
    def click_position3(self):
        """Click at Position 3"""
        if not self.position3:
            return
        
        try:
            # Move mouse to position3 and left-click
            pyautogui.moveTo(self.position3[0], self.position3[1])
            pyautogui.leftClick()
            
            # Wait for the specified click delay
            time.sleep(self.click_delay)
            
        except Exception as e:
            print(f"Error clicking position3: {str(e)}")
    
    def compare_images(self, img1, img2, threshold=0.80):
        """Compare two images and return True if they are similar enough"""
        try:
            # Convert PIL images to numpy arrays
            img1_np = np.array(img1)
            img2_np = np.array(img2)
            
            # Convert to grayscale
            img1_gray = cv2.cvtColor(img1_np, cv2.COLOR_RGB2GRAY)
            img2_gray = cv2.cvtColor(img2_np, cv2.COLOR_RGB2GRAY)
            
            # Resize if the dimensions don't match
            if img1_gray.shape != img2_gray.shape:
                img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
            
            # Calculate structural similarity
            score, _ = ssim(img1_gray, img2_gray, full=True)
            print(f"Similarity score: {score}")
            
            # Return True if the score is above the threshold
            return score > threshold
        
        except Exception as e:
            print(f"Error in image comparison: {str(e)}")
            
            # Fall back to simpler comparison
            return self.simple_compare(img1, img2)
    
    def simple_compare(self, img1, img2, threshold=0.90):
        """Fallback simpler image comparison method"""
        try:
            # Convert PIL images to numpy arrays
            img1_np = np.array(img1)
            img2_np = np.array(img2)
            
            # Resize if the dimensions don't match
            if img1_np.shape != img2_np.shape:
                img2_np = cv2.resize(img2_np, (img1_np.shape[1], img1_np.shape[0]))
            
            # Calculate absolute difference
            diff = cv2.absdiff(img1_np, img2_np)
            
            # Calculate non-zero percentage (difference)
            non_zero = np.count_nonzero(diff)
            total_pixels = diff.size
            similarity = 1.0 - (non_zero / total_pixels)
            
            print(f"Simple similarity: {similarity}")
            return similarity > threshold
            
        except Exception as e:
            print(f"Error in simple comparison: {str(e)}")
            return False
    
    def reset_ui(self):
        """Reset the UI after monitoring is done"""
        self.monitoring = False
        self.start_btn.config(text="Start Monitoring")
        self.image1_btn.config(state=tk.NORMAL)
        self.image2_btn.config(state=tk.NORMAL)
        self.image3_btn.config(state=tk.NORMAL)  # Enable image3 button
        self.pos3_btn.config(state=tk.NORMAL)
    
    def update_ui_from_settings(self):
        """Update UI elements to reflect loaded settings"""
        settings_loaded = False
        
        # Update image1 position label
        if self.image1_position:
            self.image1_pos_label.config(text=f"({self.image1_position[0]}, {self.image1_position[1]}) to ({self.image1_position[2]}, {self.image1_position[3]})")
            settings_loaded = True
            
            # Display thumbnail if we have image1
            if self.image1:
                thumbnail = self.image1.copy()
                thumbnail.thumbnail((100, 100))
                self.image1_thumbnail = ImageTk.PhotoImage(thumbnail)
                
                if not hasattr(self, 'image1_display'):
                    self.image1_display = Label(self.root)
                    self.image1_display.place(x=350, y=50)
                    
                self.image1_display.config(image=self.image1_thumbnail)
        
        # Update image2 position label
        if self.image2_position:
            self.image2_pos_label.config(text=f"({self.image2_position[0]}, {self.image2_position[1]}) to ({self.image2_position[2]}, {self.image2_position[3]})")
            settings_loaded = True
            
            # Display thumbnail if we have image2
            if self.image2:
                thumbnail = self.image2.copy()
                thumbnail.thumbnail((100, 100))
                self.image2_thumbnail = ImageTk.PhotoImage(thumbnail)
                
                if not hasattr(self, 'image2_display'):
                    self.image2_display = Label(self.root)
                    self.image2_display.place(x=350, y=160)
                    
                self.image2_display.config(image=self.image2_thumbnail)

        # Update image3 position label
        if self.image3_position:
            self.image3_pos_label.config(text=f"({self.image3_position[0]}, {self.image3_position[1]}) to ({self.image3_position[2]}, {self.image3_position[3]})")
            settings_loaded = True
            
            # Display thumbnail if we have image3
            if self.image3:
                thumbnail = self.image3.copy()
                thumbnail.thumbnail((100, 100))
                self.image3_thumbnail = ImageTk.PhotoImage(thumbnail)
                
                if not hasattr(self, 'image3_display'):
                    self.image3_display = Label(self.root)
                    self.image3_display.place(x=350, y=270)
                    
                self.image3_display.config(image=self.image3_thumbnail)
        
        # Update position3 label
        if self.position3:
            self.pos3_label.config(text=f"({self.position3[0]}, {self.position3[1]})")
            settings_loaded = True
        
        # Update sliders for delay settings
        self.loop_delay_slider.set(self.loop_delay)
        self.click_delay_slider.set(self.click_delay)
        
        # Update settings status
        if settings_loaded:
            self.settings_label.config(text="Settings loaded successfully")
            self.status_label.config(text="Ready with saved settings")
        else:
            self.settings_label.config(text="No saved settings found")
    
    def save_settings_with_feedback(self):
        """Save settings and provide feedback to the user"""
        # Check if we have anything to save
        if not (self.image1 and self.image2 and self.image3 and self.position3):
            missing = []
            if not self.image1:
                missing.append("Image 1")
            if not self.image2:
                missing.append("Image 2")
            if not self.image3:
                missing.append("Image 3")
            if not self.position3:
                missing.append("Position 3")
                
            messagebox.showwarning("Missing Selections", 
                                 f"Please select the following before saving: {', '.join(missing)}")
            return
        
        # Save settings
        if self.save_settings():
            self.settings_label.config(text="Settings saved successfully")
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.\n\nThey will be automatically loaded the next time you start the application.")
        else:
            messagebox.showerror("Error", "Failed to save settings.")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            # Save settings before exiting
            self.save_settings()
            self.monitoring = False
            self.root.destroy()

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Enable DPI awareness for better display on high-DPI screens
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Create the main window
    root = tk.Tk()
    app = AdvancedScreenClicker(root)
    
    # Set icon if available
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    # Start the main loop
    root.mainloop()
