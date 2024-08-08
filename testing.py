import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk, ImageDraw
import threading
import time
import os
from ultralytics import YOLO
import pyttsx3

class VideoCaptureApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.current_theme = "dark"  # Initial theme setting
        
    
        # Initial dark mode setup
        self.set_theme("dark")
        
        
         # Set the background color of the root window
        self.window.configure(bg="#1E1E1E")
        
        # Create the home frame with reduced padding
        self.home_frame = tk.Frame(self.window, bg="#1E1E1E")
        self.home_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Adjust padx and pady as needed
        
        # Create and place the title label
        title_label = tk.Label(self.home_frame, text="Safety Scout", font=("Arial", 30, "bold"), fg="white", bg="#1E1E1E", highlightbackground="#1E1E1E", highlightcolor="#1E1E1E")
        title_label.pack(fill=tk.X, pady=5)
        
        # Create the toggle theme button
        self.toggle_theme_button = tk.Button(self.home_frame, text="🌓Light", command=self.toggle_theme, font=("Arial", 15), width=6, height=1, bd=0, bg="#4A90E2", fg="white", activebackground="#4A90E2", activeforeground="white")
        self.toggle_theme_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-20, y=30)
        

        # Initialize video capture variables
        self.cap = None
        self.thread = None
        self.is_capturing = False

        # Create the frames
        self.create_frames()

        # Load the YOLOv8 model for fire and smoke detection
        self.model = YOLO('Z:/runs/detect/train2/weights/best.pt')
       

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Start capturing images every 2 minutes
        self.start_auto_capture()

        # Run the main loop
        self.window.mainloop()
        
        
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.set_theme("light")
            self.current_theme="light"
            self.toggle_theme_button.config(text="🌑Dark")
        else:
            self.set_theme("dark")
            self.current_theme="dark"
            self.toggle_theme_button.config(text="🌓Light")


    
    def set_theme(self, theme):
        self.current_theme = theme
        if theme == "dark":
            self.bg_color = "#1E1E1E"
            self.text_color = "white"
        elif theme == "light":
            self.bg_color = "white"
            self.text_color = "black"
        
        # Update all widgets with new colors
        self.update_theme_widgets(self.window)
        # Update root window background color
        self.window.configure(bg=self.bg_color)
    
    def update_theme_widgets(self, parent):
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=self.bg_color)
                self.update_theme_widgets(widget)
            elif isinstance(widget, tk.Label):
                widget.config(bg=self.bg_color, fg=self.text_color)
            elif isinstance(widget, tk.Button):
                widget.config(bg="#4A90E2", fg="white", activebackground="#4A90E2", activeforeground="white")
            elif isinstance(widget, tk.Checkbutton):
                widget.config(bg=self.bg_color, fg=self.text_color, selectcolor=self.bg_color, activeforeground=self.text_color)
            elif isinstance(widget, tk.Text):
                widget.config(bg="white" if self.current_theme == "light" else "#333333", fg=self.text_color)


    def create_frames(self):
        
        
        # Create the home frame
        self.home_frame = tk.Frame(self.window, bg=self.bg_color)
      
        self.home_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        

        # Create and place the welcome message
        welcome_message = tk.Label(self.home_frame, text="Welcome To SafetyScout", font=("Arial", 24, "bold"), bg=self.bg_color, fg="white")
        welcome_message.pack(pady=5)

        # Community message
        community_message = tk.Label(self.home_frame, text="The SafetyScout community is dedicated to helping you stay safe by detecting fire\nand smoke hazards in your area and providing essential safety tips and guidelines.", 
                                     font=("Arial", 14), justify=tk.LEFT, bg=self.bg_color, fg="white")
        community_message.pack(pady=5)
        
        
        # Camera permission checkbox
        self.camera_permission_var = tk.BooleanVar()
        camera_permission_checkbutton = tk.Checkbutton(self.home_frame, text="Grant permission to access your Camera", variable=self.camera_permission_var, 
                                                       bg=self.bg_color, font=("Arial", 12, "bold") ,fg="white", selectcolor=self.bg_color, activeforeground="white")
        camera_permission_checkbutton.pack(anchor=tk.W, padx=220, pady=20)

        # Let's Get Scanning button
        scanning_button = tk.Button(self.home_frame, text="Let's Get Scanning", command=self.grant_camera_permission, width=20, height=2, 
                                    bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        scanning_button.pack(anchor=tk.W, padx=220, pady=10)



        # Create Quick Access section
        quick_access_label = tk.Label(self.home_frame, text="Quick Access", font=("Arial", 18, "bold"), bg=self.bg_color, fg="white")
        quick_access_label.pack(anchor=tk.W, padx=220, pady=10)

        quick_access_frame = tk.Frame(self.home_frame, bg=self.bg_color)
        quick_access_frame.pack(anchor=tk.W)

        # Safety Guidelines button
        safety_guidelines_button_quick = tk.Button(quick_access_frame, text="Safety Guidelines", command=self.show_safety_page, height=2, width=20, 
                                                  bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        safety_guidelines_button_quick.pack(anchor=tk.W, padx=220, pady=10)

        # Report a Hazard button
        report_hazard_button_quick = tk.Button(quick_access_frame, text="Report a Hazard", command=self.show_report_page, height=2, width=20, 
                                               bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        report_hazard_button_quick.pack(anchor=tk.W, padx=220, pady=10)
        
        # Help and Feedback button
        report_hazard_button_quick = tk.Button(quick_access_frame, text="Help and Feedback", command=self.show_Help_page, height=2, width=20, 
                                               bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        report_hazard_button_quick.pack(anchor=tk.W, padx=220, pady=10)

        # Create a space for the image on the right side
        self.image_frame = tk.Frame(self.home_frame, width=600, height=500, bg=self.bg_color)
        self.image_frame.pack_propagate(False)
        self.image_frame.place(relx=0.7, rely=0.7, anchor=tk.CENTER)

        # Placeholder label for the image
        self.image_label = tk.Label(self.image_frame, text="", bg="#1E1E1E", font=("Arial", 16, "italic"), fg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Create and place the navigation buttons at the bottom
        nav_frame = tk.Frame(self.window, bg=self.bg_color)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Home button
        home_button = tk.Button(nav_frame, text="Home", width=20, bg="#4A90E2", fg="white", command=self.show_home_page, font=("Arial", 12, "bold"))
        home_button.pack(side=tk.LEFT, padx=(20, 10), expand=True, fill=tk.X)

        # Report a Hazard button
        report_hazard_button_nav = tk.Button(nav_frame, text="Report a Hazard", width=20, bg="#4A90E2", fg="white", command=self.show_report_page, font=("Arial", 12, "bold"))
        report_hazard_button_nav.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Safety Guidelines button
        safety_guidelines_button_nav = tk.Button(nav_frame, text="Safety Guidelines", width=20, bg="#4A90E2", fg="white", command=self.show_safety_page, font=("Arial", 12, "bold"))
        safety_guidelines_button_nav.pack(side=tk.LEFT, padx=(10, 20), expand=True, fill=tk.X)
        
        
        # Help and Support button
        help_guidelines_button_nav = tk.Button(nav_frame, text="Help and Feedback", width=20, bg="#4A90E2", fg="white", command=self.show_Help_page, font=("Arial", 12, "bold"))
        help_guidelines_button_nav.pack(side=tk.LEFT, padx=(10, 20), expand=True, fill=tk.X)


        # Create the report frame
        self.report_frame = tk.Frame(self.window, bg=self.bg_color)

        # Create and place the report page elements
        report_title_label = tk.Label(self.report_frame, text="Report a Hazard", font=("Arial", 24, "underline"), bg=self.bg_color, fg="white")
        report_title_label.pack(pady=20)
        
        report_title_label = tk.Label(self.report_frame, text="Instructions: ", font=("Arial", 18, "underline"), bg=self.bg_color, fg="white")
        report_title_label.pack(pady=20)


        instructions_label = tk.Label(self.report_frame, text="In the description below provide detailed and accurate information about the hazard you are reporting,so that it can be addressed effectively.", 
                                      font=("Arial", 16), justify=tk.LEFT, bg=self.bg_color, fg="white")
        instructions_label.pack(pady=10)

        description_label = tk.Label(self.report_frame, text="Description", font=("Arial", 18, "underline"), bg=self.bg_color, fg="white")
        description_label.pack(pady=5)
        

        self.description_text = tk.Text(self.report_frame, height=10, width=100)
        self.description_text.insert(tk.END, "Type of hazard ...\nLocation ...\nCasualties (if Known) ...")
        self.description_text.pack(pady=10)

        upload_label = tk.Label(self.report_frame, text="Upload Images", font=("Arial", 16, "underline"), bg=self.bg_color, fg="white")
        upload_label.pack(pady=10)

        upload_button = tk.Button(self.report_frame, text="Upload an image in pdf, jpeg, png format", command=self.upload_image, width=40, height=2, 
                                  bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        upload_button.pack(pady=10)

        submit_button = tk.Button(self.report_frame, text="Submit", command=self.submit_hazard, width=20, height=2, 
                                  bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        submit_button.pack(pady=10)

        

        # Create the safety frame
        self.safety_frame = tk.Frame(self.window, bg=self.bg_color)
        # Create and place the safety title
        safety_title_label = tk.Label(self.safety_frame, text="Safety Scout - Safety Guidelines", font=("Arial", 24), fg="#4A90E2", bg=self.bg_color)
        safety_title_label.pack(pady=10)

        # Fire Safety section

        fire_safety_label = tk.Label(self.safety_frame, text="Fire Safety", font=("Arial", 20, "underline"), bg=self.bg_color, fg="white")
        fire_safety_label.pack(pady=5)
        fire_safety_frame = tk.Frame(self.safety_frame, bg=self.bg_color)
        fire_safety_frame.pack(pady=10, padx=10, fill="both")

        
# Load and display the fire safety image
        fire_image_path = "fire.png"  # Replace with the path to your fire image
        fire_image = Image.open(fire_image_path)
        fire_image = fire_image.resize((600, 200), Image.LANCZOS)  # Resize as needed
        fire_image_tk = ImageTk.PhotoImage(fire_image)
        fire_image_label = tk.Label(fire_safety_frame, image=fire_image_tk, bg=self.bg_color)
        fire_image_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")  # Align image to the right
        fire_image_label.image = fire_image_tk  # Keep a reference to avoid garbage collection

# Fire Safety information text
        
        fire_safety_info = tk.Label(fire_safety_frame, text=("Place smoke alarms on every level of your home, inside bedrooms, and outside sleeping areas and Plan\n"
            "Escape Know How to Use a Fire Extinguisher Remember PASS: Pull the pin, Aim low, Squeeze the\n"
            "handle, Sweep side to side. Closing doors behind you as you leave can slow the spread of fire and\n"
            "smoke. Stop, Drop, and Roll If your clothes catch fire, stop immediately, drop to the ground, and roll\n"
            "over to smother the flames."), font=("Arial", 15), justify=tk.LEFT, bg=self.bg_color, fg="white")
        fire_safety_info.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # Align text to the left

# Smoke Safety section
        smoke_safety_label = tk.Label(self.safety_frame, text="Smoke Safety", font=("Arial", 20, "underline"), bg=self.bg_color, fg="white")
        smoke_safety_label.pack(pady=5)
        smoke_safety_frame = tk.Frame(self.safety_frame, bg=self.bg_color)
        smoke_safety_frame.pack(pady=10, padx=10, fill="both")

# Load and display the smoke safety image
        
        smoke_image_path = "smoke.png"  # Replace with the path to your smoke image
        smoke_image = Image.open(smoke_image_path)
        smoke_image = smoke_image.resize((600, 200), Image.LANCZOS)  # Resize as needed
        smoke_image_tk = ImageTk.PhotoImage(smoke_image)
        smoke_image_label = tk.Label(smoke_safety_frame, image=smoke_image_tk, bg=self.bg_color)
        smoke_image_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")  # Align image to the right
        smoke_image_label.image = smoke_image_tk  # Keep a reference to avoid garbage collection

# Smoke Safety information text
        
        smoke_safety_info = tk.Label(smoke_safety_frame, text=("Ensure smoke detectors are on every level of your home, particularly in bedrooms and hallways. If you\n"
            "must move through smoke, cover your mouth and nose with a cloth (preferably wet) to help filter out some\n"
            "of the smoke particles. Ensure everyone knows all the exits in the building and practices how to get to\n"
            "them quickly and safely. If you cannot escape, signal for help at a window by using a flashlight or waving a\n"
            "cloth. Open a window slightly to let out smoke if you are trapped and awaiting rescue, but be cautious of\n"
            "letting in more smoke. Make sure everyone in your household understands the dangers of smoke and how\n"
            "to react if they encounter it."), font=("Arial", 15), justify=tk.LEFT, bg=self.bg_color, fg="white")
        smoke_safety_info.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # Align text to the left
        
        
        
        
        
        
         # Create the Help and Feedback frame
        self.Help_frame = tk.Frame(self.window, bg=self.bg_color)

# Create and place the Help title
        Help_title_label = tk.Label(self.Help_frame, text="Safety Scout - Help and Feedback", font=("Arial", 24), fg="#4A90E2", bg=self.bg_color)
        Help_title_label.pack(pady=5)

# Help section

        RecordHelp_label = tk.Label(self.Help_frame, text="How to start Recording? \nIn order to begin your recording: \n1. Check the Grant permission check box to access Camera box. \n2. Click on the Get Started button.", font=("Arial", 15), bg=self.bg_color, fg="white")
        RecordHelp_label.pack(pady=5)
        RecordHelp_frame = tk.Frame(self.Help_frame, bg=self.bg_color)
        RecordHelp_frame.pack(pady=10, padx=5, fill="both")
        

# Help information text
        
      
        ReportHelp_label = tk.Label(self.Help_frame, text="How to submit a Report? \nIn order to submit your report: \n1. Enter the necessary and accurate details of the Fire Hazard like casualities and location. \n2. Upload a clear image of the accident in the allowed formats and Submit.", font=("Arial", 15), bg=self.bg_color, fg="white")
        ReportHelp_label.pack(pady=5)
        ReportHelp_frame = tk.Frame(self.Help_frame, bg=self.bg_color)
        ReportHelp_frame.pack(pady=10, padx=10, fill="both")
    

# Feedback section
        description_label = tk.Label(self.Help_frame, text="Feedback!\nThank you for taking the time to provide your feedback. Your insights and suggestions are valuable to us. \nThank you for your support and for helping us grow.", font=("Arial", 15), bg=self.bg_color, fg="white")
        description_label.pack(pady=5)
        
        self.description_text = tk.Text(self.Help_frame, height=10, width=100)
        self.description_text.insert(tk.END, "")
        self.description_text.pack(pady=10)
        
        submit_button = tk.Button(self.Help_frame, text="Submit", command=self.submit_Feedback, width=20, height=2, 
                                  bg="#4A90E2", fg="white", font=("Arial", 12, "bold"))
        submit_button.pack(pady=5)
       
        # Forward button (top right corner)
        forward_button = tk.Button(self.home_frame, text="→", command=self.show_report_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        forward_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-10, y=10)

        # Back button (top left corner) in report frame
        back_button_report = tk.Button(self.report_frame, text="←", command=self.show_home_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        back_button_report.place(relx=0.0, rely=0.0, anchor=tk.NW, x=10, y=10)

        # Forward button (top right corner) in report frame
        forward_button_report = tk.Button(self.report_frame, text="→", command=self.show_safety_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        forward_button_report.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-10, y=10)

        # Back button (top left corner) in safety frame
        back_button_safety = tk.Button(self.safety_frame, text="←", command=self.show_report_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        back_button_safety.place(relx=0.0, rely=0.0, anchor=tk.NW, x=10, y=10)

        # Forward button (top right corner) in safety frame
        forward_button_safety = tk.Button(self.safety_frame, text="→", command=self.show_Help_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        forward_button_safety.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-10, y=10)
        
        # Back button (top left corner) in safety frame
        back_button_safety = tk.Button(self.Help_frame, text="←", command=self.show_safety_page, font=("Arial", 15, "bold"), bg="#4A90E2", fg="white")
        back_button_safety.place(relx=0.0, rely=0.0, anchor=tk.NW, x=10, y=10)
        
        

    def grant_camera_permission(self):
        if not self.camera_permission_var.get():
            messagebox.showinfo("Camera Permission", "Please grant permission to access your Camera.")
            return
        
        messagebox.showinfo("Camera Permission", "Camera access granted!")

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Failed to open webcam.")
            return
        
        # Start video capture in a separate thread
        self.is_capturing = True
        self.thread = threading.Thread(target=self.update_video)
        self.thread.daemon = True
        self.thread.start()

    def update_video(self):
        while self.is_capturing:
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to capture frame.")
                break
            
            # Convert the frame from OpenCV BGR format to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize the frame to fit into the image_label
            frame_resized = cv2.resize(frame_rgb, (600, 500))
            
            # Convert the resized frame to ImageTk format
            img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))

            # Update the image_label with the new frame
            self.image_label.img = img
            self.image_label.config(image=img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)  # Adjust delay as needed

    def start_auto_capture(self):
        auto_capture_thread = threading.Thread(target=self.auto_capture_thread_func)
        auto_capture_thread.daemon = True
        auto_capture_thread.start()

    def auto_capture_thread_func(self):
        while True:
            if self.is_capturing:
                # Delete the previous 'image.jpg' if it exists
                if os.path.exists("image.jpg"):
                    os.remove("image.jpg")

                ret, frame = self.cap.read()
                if ret:
                    # Perform object detection
                    results = self.model(frame)
                    annotated_frame = results[0].plot()

                    # Get detected object names
                    detected_objects = [self.model.names[int(box.cls)] for box in results[0].boxes]
                    if detected_objects:
                        self.announce_detected_objects(detected_objects)

                    # Save the annotated frame as 'image.jpg'
                    cv2.imwrite("image.jpg", annotated_frame)
                    
                    # Display the annotated image in the GUI
                    self.display_image(annotated_frame)
                    
                    # Display a message indicating image capture
                    print("Image captured, annotated, and saved: image.jpg")

            # Wait for 5 sec before capturing the next image
            time.sleep(5)

    def announce_detected_objects(self, objects):
        objects_str = ', '.join(objects)
        self.engine.say(f"Detected: {objects_str}")
        self.engine.runAndWait()

    def display_image(self, image):
        # Convert the frame from OpenCV BGR format to RGB format
        frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize the frame to fit into the image_label
        frame_resized = cv2.resize(frame_rgb, (400, 400))
        
        # Convert the resized frame to ImageTk format
        img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))

        # Update the image_label with the new frame
        self.image_label.img = img
        self.image_label.config(image=img)

    def show_home_page(self):
        self.report_frame.pack_forget()
        self.safety_frame.pack_forget()
        self.Help_frame.pack_forget()
        self.home_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def show_report_page(self):
        self.report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.home_frame.pack_forget()
        self.safety_frame.pack_forget()
        self.Help_frame.pack_forget()

    def show_safety_page(self):
        self.safety_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.home_frame.pack_forget()
        self.report_frame.pack_forget()
        self.Help_frame.pack_forget()
        
    def show_Help_page(self):
        self.Help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.home_frame.pack_forget()
        self.report_frame.pack_forget() 
        self.safety_frame.pack_forget()   

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.pdf *.jpeg *.jpg *.png")])
        if file_path:
            print(file_path)
            messagebox.showinfo("Image Upload", f"Image uploaded: {file_path}")



    def submit_hazard(self):
        messagebox.showinfo("Submit", "Hazard report submitted!")
        
    def submit_Feedback(self):
        messagebox.showinfo("Submit", "Thank You for your valuable Feedback!")

# Create the main window
root = tk.Tk()
root.title("Safety Scout")
root.geometry("1200x800")

# Initialize the application
app = VideoCaptureApp(root, "Safety Scout")

# Run the main loop
root.mainloop()

