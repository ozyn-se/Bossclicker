import sys
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, Label, Button, Frame
import pyautogui
import numpy as np
from PIL import Image, ImageTk, ImageGrab
from skimage.metrics import structural_similarity as ssim
import cv2
import json
import pickle
import base64
from io import BytesIO

class ScreenClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Tribute Portal Clicker")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Settings file path
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        
        # Initialize variables
        self.target_image = None
        self.target_position = None
        self.click_position = None
        self.final_click_position = None
        self.monitoring = False
        self.monitor_thread = None
        
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
            
            # Save target position
            if self.target_position:
                settings["target_position"] = list(self.target_position)
            
            # Save click positions
            if self.click_position:
                settings["click_position"] = list(self.click_position)
            
            if self.final_click_position:
                settings["final_click_position"] = list(self.final_click_position)
            
            # Save target image if it exists
            if self.target_image:
                # Convert image to base64 string
                buffered = BytesIO()
                self.target_image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                settings["target_image"] = img_str
            
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
                
                # Load target position
                if "target_position" in settings:
                    self.target_position = tuple(settings["target_position"])
                
                # Load click positions
                if "click_position" in settings:
                    self.click_position = tuple(settings["click_position"])
                
                if "final_click_position" in settings:
                    self.final_click_position = tuple(settings["final_click_position"])
                
                # Load target image if it exists
                if "target_image" in settings:
                    img_data = base64.b64decode(settings["target_image"])
                    self.target_image = Image.open(BytesIO(img_data))
                
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
        
        # Instructions
        Label(main_frame, text="1. Select tribute image", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        Label(main_frame, text="2. Select open portal button position", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 5))
        Label(main_frame, text="3. Select accept position", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 5))
        Label(main_frame, text="4. Start monitoring", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        # Buttons frame
        btn_frame = Frame(main_frame)
        btn_frame.grid(row=4, column=0, pady=10)
        
        # Buttons
        self.target_btn = Button(btn_frame, text="Select Tribute Image", command=self.select_target, width=20)
        self.target_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.click_btn = Button(btn_frame, text="Select Portal Button", command=self.select_click_position, width=20)
        self.click_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.final_click_btn = Button(btn_frame, text="Select Accept Button", command=self.select_final_click_position, width=20)
        self.final_click_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.start_btn = Button(btn_frame, text="Start Monitoring", command=self.toggle_monitoring, width=20)
        self.start_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.save_btn = Button(btn_frame, text="Save Settings", command=self.save_settings_with_feedback, width=20)
        self.save_btn.grid(row=2, column=0, padx=5, pady=5)
        
        self.exit_btn = Button(btn_frame, text="Exit", command=self.exit_app, width=20)
        self.exit_btn.grid(row=2, column=1, padx=5, pady=5)
        
        # Status frame
        status_frame = Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=5, column=0, sticky="ew", pady=10)
        
        # Status labels
        Label(status_frame, text="Status:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.status_label = Label(status_frame, text="Ready", font=("Arial", 9))
        self.status_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        Label(status_frame, text="Tribute Image:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_pos_label = Label(status_frame, text="Not selected", font=("Arial", 9))
        self.target_pos_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        Label(status_frame, text="Portal Button:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.click_pos_label = Label(status_frame, text="Not selected", font=("Arial", 9))
        self.click_pos_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        Label(status_frame, text="Accept Button:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.final_click_pos_label = Label(status_frame, text="Not selected", font=("Arial", 9))
        self.final_click_pos_label.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Settings status
        Label(status_frame, text="Settings:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.settings_label = Label(status_frame, text="No saved settings", font=("Arial", 9))
        self.settings_label.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Update UI with loaded settings if any
        self.update_ui_from_settings()
    
    def select_target(self):
        """Capture a region of the screen as the target image"""
        self.root.iconify()  # Minimize window
        time.sleep(1)  # Give user time to prepare
        
        # Create a transparent fullscreen window
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.configure(bg='black')
        overlay.lift()  # Make sure it's on top
        overlay.focus_force()  # Force focus to this window
        
        # Variables to store rectangle coordinates
        start_x = start_y = end_x = end_y = 0
        rect_id = None
        is_drawing = False
        
        # Canvas for drawing
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions label
        instructions = tk.Label(canvas, text="Click and drag to select an area", 
                              font=("Arial", 16), bg='black', fg='white')
        instructions.place(relx=0.5, rely=0.1, anchor="center")
        
        def on_press(event):
            nonlocal start_x, start_y, rect_id, is_drawing
            start_x, start_y = event.x, event.y
            is_drawing = True
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)
            
        def on_drag(event):
            nonlocal rect_id, is_drawing
            if is_drawing and rect_id:
                canvas.delete(rect_id)
                rect_id = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline='red', width=2)
            
        def on_release(event):
            nonlocal end_x, end_y, is_drawing
            if is_drawing:
                end_x, end_y = event.x, event.y
                is_drawing = False
                # Only capture if we've actually dragged to create a rectangle
                if abs(end_x - start_x) > 5 and abs(end_y - start_y) > 5:
                    overlay.destroy()
                    self.capture_target(start_x, start_y, end_x, end_y)
        
        # Bind events to the canvas
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Bind escape key to close the overlay
        overlay.bind("<Escape>", lambda e: overlay.destroy())
        
        # Wait for overlay to be destroyed
        self.root.wait_window(overlay)
        self.root.deiconify()  # Restore main window
    
    def capture_target(self, start_x, start_y, end_x, end_y):
        """Capture the selected region as the target image"""
        # Ensure coordinates are in the right order
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        right = max(start_x, end_x)
        bottom = max(start_y, end_y)
        
        # Store the target position
        self.target_position = (left, top, right, bottom)
        self.target_pos_label.config(text=f"({left}, {top}) to ({right}, {bottom})")
        
        # Capture the image
        self.target_image = ImageGrab.grab(bbox=self.target_position)
        
        # Show confirmation
        messagebox.showinfo("Target Selected", "Target image has been captured!")
        self.status_label.config(text="Target image captured")
    
    def select_click_position(self):
        """Select the position to click after the target image is found"""
        self.root.iconify()  # Minimize window
        time.sleep(1)  # Give user time to prepare
        
        # Create a transparent fullscreen window
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.configure(bg='black')
        overlay.lift()  # Make sure it's on top
        overlay.focus_force()  # Force focus to this window
        
        # Create canvas for drawing
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add crosshair cursor
        overlay.config(cursor="crosshair")
        
        # Label with instructions
        instructions = Label(canvas, text="Click on the position where you want to click after the target is found", 
                     font=("Arial", 16), bg='black', fg='white')
        instructions.place(relx=0.5, rely=0.1, anchor="center")
        
        # Add a visual marker for the current mouse position
        marker_h = None
        marker_v = None
        position_label = Label(canvas, text="", font=("Arial", 12), bg='black', fg='white')
        position_label.place(relx=0.5, rely=0.9, anchor="center")
        
        def on_mouse_move(event):
            nonlocal marker_h, marker_v
            # Update position label
            position_label.config(text=f"Position: ({event.x}, {event.y})")
            
            # Update crosshair markers
            if marker_h:
                canvas.delete(marker_h)
            if marker_v:
                canvas.delete(marker_v)
                
            # Create horizontal and vertical lines
            marker_h = canvas.create_line(0, event.y, overlay.winfo_width(), event.y, fill="red", dash=(4, 4))
            marker_v = canvas.create_line(event.x, 0, event.x, overlay.winfo_height(), fill="red", dash=(4, 4))
        
        def on_click(event):
            self.click_position = (event.x, event.y)
            overlay.destroy()
        
        # Bind events
        canvas.bind("<Motion>", on_mouse_move)
        canvas.bind("<Button-1>", on_click)
        overlay.bind("<Escape>", lambda e: overlay.destroy())
        
        # Wait for overlay to be destroyed
        self.root.wait_window(overlay)
        self.root.deiconify()  # Restore main window
        
        if self.click_position:
            self.click_pos_label.config(text=f"({self.click_position[0]}, {self.click_position[1]})")
            messagebox.showinfo("Click Position", f"Click position set to {self.click_position}")
            self.status_label.config(text="Click position set")
    
    def select_final_click_position(self):
        """Select the final position to click after the first click"""
        self.root.iconify()  # Minimize window
        time.sleep(1)  # Give user time to prepare
        
        # Create a transparent fullscreen window
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.configure(bg='black')
        overlay.lift()  # Make sure it's on top
        overlay.focus_force()  # Force focus to this window
        
        # Create canvas for drawing
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add crosshair cursor
        overlay.config(cursor="crosshair")
        
        # Label with instructions
        instructions = Label(canvas, text="Click on the position for the final click", 
                     font=("Arial", 16), bg='black', fg='white')
        instructions.place(relx=0.5, rely=0.1, anchor="center")
        
        # Add a visual marker for the current mouse position
        marker_h = None
        marker_v = None
        position_label = Label(canvas, text="", font=("Arial", 12), bg='black', fg='white')
        position_label.place(relx=0.5, rely=0.9, anchor="center")
        
        def on_mouse_move(event):
            nonlocal marker_h, marker_v
            # Update position label
            position_label.config(text=f"Position: ({event.x}, {event.y})")
            
            # Update crosshair markers
            if marker_h:
                canvas.delete(marker_h)
            if marker_v:
                canvas.delete(marker_v)
                
            # Create horizontal and vertical lines
            marker_h = canvas.create_line(0, event.y, overlay.winfo_width(), event.y, fill="green", dash=(4, 4))
            marker_v = canvas.create_line(event.x, 0, event.x, overlay.winfo_height(), fill="green", dash=(4, 4))
        
        def on_click(event):
            self.final_click_position = (event.x, event.y)
            overlay.destroy()
        
        # Bind events
        canvas.bind("<Motion>", on_mouse_move)
        canvas.bind("<Button-1>", on_click)
        overlay.bind("<Escape>", lambda e: overlay.destroy())
        
        # Wait for overlay to be destroyed
        self.root.wait_window(overlay)
        self.root.deiconify()  # Restore main window
        
        if self.final_click_position:
            self.final_click_pos_label.config(text=f"({self.final_click_position[0]}, {self.final_click_position[1]})")
            messagebox.showinfo("Final Click Position", f"Final click position set to {self.final_click_position}")
            self.status_label.config(text="Final click position set")
    
    def toggle_monitoring(self):
        """Start or stop the continuous monitoring process"""
        if not self.monitoring:
            # Check if all required selections are made
            if not self.target_image or not self.target_position or not self.click_position or not self.final_click_position:
                messagebox.showerror("Error", "Please select target image, click position, and final click position first!")
                return
            
            # Start monitoring
            self.monitoring = True
            self.start_btn.config(text="Stop Monitoring")
            self.status_label.config(text="Starting continuous monitoring...")
            
            # Disable other buttons while monitoring
            self.target_btn.config(state=tk.DISABLED)
            self.click_btn.config(state=tk.DISABLED)
            self.final_click_btn.config(state=tk.DISABLED)
            
            # Show info about continuous mode
            messagebox.showinfo("Continuous Monitoring", "The application will now continuously monitor for the target image every 5 seconds. When found, it will perform the clicks and continue monitoring without interruption.")
            
            # Start the monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_screen)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        else:
            # Stop monitoring
            self.monitoring = False
            self.start_btn.config(text="Start Monitoring")
            self.status_label.config(text="Monitoring stopped")
            
            # Re-enable buttons
            self.target_btn.config(state=tk.NORMAL)
            self.click_btn.config(state=tk.NORMAL)
    
    def monitor_screen(self):
        """Monitor the screen for the target image"""
        try:
            # Store the original target image for comparison
            self.original_target = self.target_image.copy()
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Monitoring for target image..."))
            
            match_count = 0  # Counter for consecutive matches to avoid false positives
            last_action_time = 0  # Track when the last action was performed
            check_interval = 5.0  # Check every 5 seconds
            
            while self.monitoring:
                current_time = time.time()
                
                # Capture the current state of the target area
                current_image = ImageGrab.grab(bbox=self.target_position)
                
                # Compare with the target image
                is_match = self.compare_images(self.original_target, current_image)
                
                if is_match:
                    match_count += 1
                    self.root.after(0, lambda count=match_count: self.status_label.config(text=f"Potential match found ({count}/3)..."))
                    
                    # Require 3 consecutive matches to avoid false positives
                    if match_count >= 3:
                        # Check if enough time has passed since last action
                        if current_time - last_action_time >= check_interval:
                            # Target found, perform actions
                            self.root.after(0, lambda: self.status_label.config(text="Target found! Performing actions..."))
                            self.perform_actions()
                            
                            # Update last action time
                            last_action_time = current_time
                            
                            # Reset match counter after performing actions
                            match_count = 0
                else:
                    # Reset match counter if no match
                    match_count = 0
                    self.root.after(0, lambda: self.status_label.config(text="Monitoring for target image..."))
                
                # Sleep to avoid high CPU usage
                time.sleep(0.5)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            # Reset UI when done
            if self.root.winfo_exists():  # Check if root window still exists
                self.root.after(0, self.reset_ui)
    
    def compare_images(self, img1, img2, threshold=0.80):
        """Compare two images and return True if they are similar enough using structural similarity"""
        try:
            # Convert images to numpy arrays
            img1_array = np.array(img1)
            img2_array = np.array(img2)
            
            # Ensure the images are the same size
            if img1_array.shape != img2_array.shape:
                print(f"Image shapes don't match: {img1_array.shape} vs {img2_array.shape}")
                return False
            
            # Convert to grayscale for better comparison
            img1_gray = cv2.cvtColor(img1_array, cv2.COLOR_RGB2GRAY)
            img2_gray = cv2.cvtColor(img2_array, cv2.COLOR_RGB2GRAY)
            
            # Calculate structural similarity index
            similarity, _ = ssim(img1_gray, img2_gray, full=True)
            
            # Also calculate MSE as a backup
            mse = np.sum((img1_array - img2_array) ** 2) / float(img1_array.size)
            mse_similarity = 1 - (mse / 255**2)
            
            # Debug info
            print(f"SSIM: {similarity:.4f}, MSE Similarity: {mse_similarity:.4f}, Threshold: {threshold}")
            
            # Only return True if the similarity is above the threshold
            is_match = similarity > threshold
            return is_match
        except Exception as e:
            print(f"Error comparing images: {str(e)}")
            # Fall back to simpler comparison if error occurs
            return self.simple_compare(img1, img2, threshold)
    
    def simple_compare(self, img1, img2, threshold=0.90):
        """Fallback simpler image comparison method"""
        # Convert images to numpy arrays
        img1_array = np.array(img1)
        img2_array = np.array(img2)
        
        # Ensure the images are the same size
        if img1_array.shape != img2_array.shape:
            return False
        
        # Calculate mean squared error
        mse = np.sum((img1_array - img2_array) ** 2) / float(img1_array.size)
        
        # Normalize to a similarity score (0-1)
        similarity = 1 - (mse / 255**2)
        
        print(f"Simple comparison: {similarity:.4f}")
        
        return similarity > threshold
    
    def perform_actions(self):
        """Perform the mouse actions once the target is found"""
        try:
            # Calculate center of target area for right click
            target_center_x = (self.target_position[0] + self.target_position[2]) // 2
            target_center_y = (self.target_position[1] + self.target_position[3]) // 2
            
            # Move to target center and right-click
            pyautogui.moveTo(target_center_x, target_center_y, duration=0.5)
            pyautogui.rightClick()
            
            # Wait a moment
            time.sleep(0.5)
            
            # Move to first click position and left-click
            pyautogui.moveTo(self.click_position[0], self.click_position[1], duration=0.5)
            pyautogui.leftClick()
            
            # Wait a moment
            time.sleep(0.5)
            
            # Move to final click position and left-click
            pyautogui.moveTo(self.final_click_position[0], self.final_click_position[1], duration=0.5)
            pyautogui.leftClick()
            
            # Update status with timestamp
            timestamp = time.strftime("%H:%M:%S")
            self.root.after(0, lambda: self.status_label.config(text=f"Actions completed at {timestamp}! Continuing to monitor..."))
            
        except Exception as e:
            error_msg = f"Failed to perform actions: {str(e)}"
            print(error_msg)
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
            # Only show error message box for critical errors
            if "failed" in str(e).lower() or "error" in str(e).lower():
                messagebox.showerror("Error", error_msg)
    
    def reset_ui(self):
        """Reset the UI after monitoring is done"""
        self.monitoring = False
        self.start_btn.config(text="Start Monitoring")
        self.target_btn.config(state=tk.NORMAL)
        self.click_btn.config(state=tk.NORMAL)
        self.final_click_btn.config(state=tk.NORMAL)
    
    def update_ui_from_settings(self):
        """Update UI elements to reflect loaded settings"""
        settings_loaded = False
        
        # Update target position label
        if self.target_position:
            self.target_pos_label.config(text=f"({self.target_position[0]}, {self.target_position[1]}) to ({self.target_position[2]}, {self.target_position[3]})")
            settings_loaded = True
        
        # Update click position label
        if self.click_position:
            self.click_pos_label.config(text=f"({self.click_position[0]}, {self.click_position[1]})")
            settings_loaded = True
        
        # Update final click position label
        if self.final_click_position:
            self.final_click_pos_label.config(text=f"({self.final_click_position[0]}, {self.final_click_position[1]})")
            settings_loaded = True
        
        # Update settings status
        if settings_loaded:
            self.settings_label.config(text="Settings loaded successfully")
            self.status_label.config(text="Ready with saved settings")
        else:
            self.settings_label.config(text="No saved settings found")
    
    def save_settings_with_feedback(self):
        """Save settings and provide feedback to the user"""
        # Check if we have anything to save
        if not self.target_position and not self.target_image:
            messagebox.showwarning("Nothing to Save", "Please select a target image before saving settings.")
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
    app = ScreenClicker(root)
    
    # Set icon if available
    try:
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    # Start the main loop
    root.mainloop()
