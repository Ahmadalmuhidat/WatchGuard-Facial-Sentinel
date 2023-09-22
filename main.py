import tkinter as tk
from tkinter import * 
from tkinter.ttk import *
import os, sys
import face_recognition
import cv2
import mysql.connector
from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter import filedialog

class CriminalFaceDetectorApp(tk.Tk):
    def __init__(self):
        self.capture_active = False
        self.video_capture = None
        self.current_page = None
        self.pages = {}
        self.showed_ids = []
        self.working_cameras = []

    def insert_new_crimnal(self, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes):
        criminal_id = None
        criminal_create_date = None
        self.cursor.execute(f"INSERT INTO criminals VALUES ({criminal_id},{criminal_first_name},{criminal_last_name},{criminal_image},{criminal_date_of_birth},{criminal_notes},{criminal_create_date})")

    def pop_match_dialog(self, criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date):
        self.showed_ids.append(criminal_id)

        dialog = tk.Toplevel()
        dialog.title("Match Found")
        dialog.geometry("600x600")

        # Load and display the user image
        criminal_image = Image.open(criminal_image)
        criminal_image.thumbnail((300, 300))  # Resize the image to a smaller size
        criminal_image = ImageTk.PhotoImage(criminal_image)

        # Create a frame for content
        content_frame = tk.Frame(dialog)
        content_frame.pack(expand=True, fill="both")

        # Create a label with a border for the image
        image_label = tk.Label(content_frame, image=criminal_image, relief="solid", borderwidth=2)
        image_label.pack()

        # Create labels with bold font for information
        bold_font = ("Arial", 12, "bold")

        tk.Label(content_frame, text=f"User ID: {criminal_id}", font=bold_font).pack()
        tk.Label(content_frame, text=f"First Name: {criminal_first_name}", font=bold_font).pack()
        tk.Label(content_frame, text=f"Last Name: {criminal_last_name}", font=bold_font).pack()
        tk.Label(content_frame, text=f"Date of Birth: {criminal_date_of_birth}", font=bold_font).pack()
        tk.Label(content_frame, text=f"Notes: {criminal_notes}", font=bold_font).pack()
        tk.Label(content_frame, text=f"Creation Date: {criminal_create_date}", font=bold_font).pack()

        # Create a frame for the close button
        footer_frame = tk.Frame(dialog)
        footer_frame.pack()

        # Close button to close the dialog
        close_button = tk.Button(footer_frame, text="Close", command=dialog.destroy)
        close_button.pack()

        # Ensure the dialog stays on top of the main window
        dialog.grab_set()
        dialog.focus_set()
        dialog.wait_window()

    def create_navbar(self, window):
        navbar = tk.Frame(window)
        navbar.pack(fill=tk.X)

        tk.Button(navbar, text="Home", command=lambda: self.show_page("Home")).pack(side=tk.LEFT)
        tk.Button(navbar, text="Criminals", command=lambda: self.show_page("Criminals")).pack(side=tk.LEFT)
        tk.Button(navbar, text="Settings", command=lambda: self.show_page("Settings")).pack(side=tk.LEFT)

    def show_page(self, name):
        if self.current_page:
             self.current_page.pack_forget()  # Hide the current page

        self.current_page = self.pages[name]
        self.current_page.pack(fill=tk.BOTH, expand=True)  # Show the selected page

    def create_page(self, window, name):
        page = tk.Frame(window)
        self.pages[name] = page

        if name == "Home":
            self.create_home_page(page)
        elif name == "Criminals":
            self.create_criminals_page(page)
        elif name == "Settings":
            self.create_settings_page(page)

    def create_home_page(self, page):
        # Configure rows and columns to center everything
        page.columnconfigure(0, weight=1)
        page.columnconfigure(1, weight=1)
        page.columnconfigure(2, weight=1)

        page.rowconfigure(0, weight=1)
        page.rowconfigure(1, weight=3)    
        page.rowconfigure(2, weight=1)

        capture_button = tk.Button(page, text="Start/Stop Capture", command=lambda: self.start_capture(self.video_label, self.result_label))
        capture_button.grid(row=0, column=1)  # Center horizontally

        video_frame = tk.Frame(page)
        video_frame.grid(row=1, column=1, sticky="nsew")  # Center horizontally and vertically

        # Create a label with a border around it
        self.video_label = tk.Label(video_frame, text="Camera is not streaming", borderwidth=2, relief="solid")
        self.video_label.pack(expand=True, fill="both")

        self.result_label = tk.Label(page, text="here the result")
        self.result_label.grid(row=2, column=1, sticky="nsew")  # Center horizontally and at the bottom

    def create_criminals_page(self, page):
        # Create a frame for adding a new criminal
        add_criminal_frame = tk.LabelFrame(page, text="Add New Criminal")
        add_criminal_frame.pack(padx=20, pady=20)

        # Create entry fields for criminal information
        criminal_id_label = tk.Label(add_criminal_frame, text="Criminal ID:")
        criminal_id_label.grid(row=0, column=0, padx=10, pady=5)
        criminal_id_entry = tk.Entry(add_criminal_frame)
        criminal_id_entry.grid(row=0, column=1, padx=10, pady=5)

        criminal_first_name_label = tk.Label(add_criminal_frame, text="First Name:")
        criminal_first_name_label.grid(row=1, column=0, padx=10, pady=5)
        criminal_first_name_entry = tk.Entry(add_criminal_frame)
        criminal_first_name_entry.grid(row=1, column=1, padx=10, pady=5)

        criminal_last_name_label = tk.Label(add_criminal_frame, text="Last Name:")
        criminal_last_name_label.grid(row=2, column=0, padx=10, pady=5)
        criminal_last_name_entry = tk.Entry(add_criminal_frame)
        criminal_last_name_entry.grid(row=2, column=1, padx=10, pady=5)

        criminal_dob_label = tk.Label(add_criminal_frame, text="Date of Birth:")
        criminal_dob_label.grid(row=3, column=0, padx=10, pady=5)
        criminal_dob_entry = tk.Entry(add_criminal_frame)
        criminal_dob_entry.grid(row=3, column=1, padx=10, pady=5)

        criminal_notes_label = tk.Label(add_criminal_frame, text="Notes:")
        criminal_notes_label.grid(row=4, column=0, padx=10, pady=5)
        criminal_notes_entry = tk.Entry(add_criminal_frame)
        criminal_notes_entry.grid(row=4, column=1, padx=10, pady=5)

        # Function to handle image upload
        def upload_image():
            file_path = filedialog.askopenfilename()
            if file_path:
                # Display the selected image in a label
                image = Image.open(file_path)
                image.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(image)
                image_label.config(image=photo)
                image_label.image = photo
                # Store the selected image path for later use
                self.image_path = file_path

        # Create a button to upload an image
        upload_button = tk.Button(add_criminal_frame, text="Upload Image", command=upload_image)
        upload_button.grid(row=5, columnspan=2, pady=10)

        # Create a label to display the uploaded image
        image_label = tk.Label(add_criminal_frame)
        image_label.grid(row=6, columnspan=2, pady=10)

        # Function to save the criminal information
        def save_criminal():
            criminal_info = {
                "Criminal ID": criminal_id_entry.get(),
                "First Name": criminal_first_name_entry.get(),
                "Last Name": criminal_last_name_entry.get(),
                "Date of Birth": criminal_dob_entry.get(),
                "Notes": criminal_notes_entry.get(),
                "Creation Date": tk.StringVar(value="Date when the criminal is created"),
                "Image Path": self.image_path if hasattr(self, "image_path") else ""
            }

            # Create a folder named "criminals" if it doesn't exist
            if not os.path.exists("criminals"):
                os.makedirs("criminals")

            # Save the criminal information to a text file (replace 'criminal.txt' with your desired file name)
            with open("criminal.txt", "w") as file:
                for key, value in criminal_info.items():
                    file.write(f"{key}: {value}\n")

            # Optionally, reset the entry fields after saving
            criminal_id_entry.delete(0, tk.END)
            criminal_first_name_entry.delete(0, tk.END)
            criminal_last_name_entry.delete(0, tk.END)
            criminal_dob_entry.delete(0, tk.END)
            criminal_notes_entry.delete(0, tk.END)
            image_label.config(image=None)

            # Create a button to save the criminal information
            save_button = tk.Button(add_criminal_frame, text="Save Criminal", command=save_criminal)
            save_button.grid(row=7, columnspan=2, pady=10)

            # Refresh the list of existing criminals
            self.display_existing_criminals()

    # def display_existing_criminals(self):
    #     # Create a frame to display existing criminals
    #     existing_criminals_frame = tk.LabelFrame(self.window, tsudo apt-get install qttools5-dev-toolsext="Existing Criminals")
    #     existing_criminals_frame.pack(padx=20, pady=20)

    #     # List all image files in the "criminals" folder
    #     criminal_images = [file for file in os.listdir("criminals") if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]

    #     for criminal_image in criminal_images:
    #         image_path = os.path.join("criminals", criminal_image)
    #         image = Image.open(image_path)
    #         image.thumbnail((100, 100))
    #         photo = ImageTk.PhotoImage(image)

    #         # Display the image
    #         tk.Label(existing_criminals_frame, image=photo).pack()

    
    def start_capture(self, video_label, result_label):
        if len(self.list_working_cameras()[1]) > 0:
            self.capture_active = True
            self.video_capture = cv2.VideoCapture(0)
            self.capture_video(video_label, result_label)  # Pass the video_label as an argument`
        else:
            messagebox.showerror("Error", "No Active Cameras Found")

    def list_working_cameras(self):
        non_working_ports = []
        dev_port = 0
        working_ports = []
        available_ports = []
        while len(non_working_ports) < 6: # if there are more than 5 non working ports stop the testing. 
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
            dev_port +=1
        return available_ports,working_ports,non_working_ports

    def create_settings_page(self, page):
        # Create a label for the settings page
        settings_label = tk.Label(page, text="Active Cameras")
        settings_label.pack()

        # Enumerate available cameras using cv2
        self.working_cameras = self.list_working_cameras()[1]  # Change the range as needed
        camera_combobox = Combobox(page, values=self.working_cameras)
        camera_combobox.set(self.working_cameras[0])  # Set the default camera
        camera_combobox.pack()
    
    def capture_video(self, video_label, result_label):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="Criminals"
            )

            if self.capture_active:
                while True:
                    ret, frame = self.video_capture.read()

                    # Display the video feed in the GUI
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(img_rgb)
                    img_tk = ImageTk.PhotoImage(image=img)

                    video_label.img = img_tk
                    video_label.config(image=img_tk)
                    video_label.update()

                    # Encode the webcam face
                    webcam_face_encoding = face_recognition.face_encodings(frame)[0]

                    self.cursor = db.cursor()
                    self.cursor.execute("SELECT * FROM criminals")
                    face_data = self.cursor.fetchall()

                    # Compare the webcam face encoding to all stored face encodings
                    for criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date in face_data:
                        load_stored_image = face_recognition.load_image_file(criminal_image)
                        stored_face_encoding = face_recognition.face_encodings(load_stored_image)[0]
                        results = face_recognition.compare_faces([stored_face_encoding], webcam_face_encoding)

                        if results[0]:
                            result_label.config(text=f"Match found for user with ID {criminal_id}")
                            # Take appropriate action for the matched user (e.g., grant access)

                            # Display the custom dialog
                            if criminal_id not in self.showed_ids:
                                self.pop_match_dialog(criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date)
                            break
                        else:
                            result_label.config(text="No match found.")

                    # Schedule the function to run again after a delay (in milliseconds)
                    self.window.after(10, self.capture_video)
        except IndexError:
            result_label.config(text="No face found.")
            self.capture_video(video_label, result_label)

    def run(self):
        try:
            self.window = tk.Tk()
            self.window.geometry("800x800")
            self.window.title("Criminals Face Detector")

            self.create_navbar(self.window)
            self.create_page(self.window, "Home")
            self.create_page(self.window, "Criminals")
            self.create_page(self.window, "Settings")

            self.show_page("Home")

            self.window.mainloop()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
        except KeyboardInterrupt:
            pass

fc = CriminalFaceDetectorApp()
fc.run()