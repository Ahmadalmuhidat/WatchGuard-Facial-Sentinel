import tkinter as tk
from tkinter import messagebox
import face_recognition
import cv2
import mysql.connector
import os, sys
from PIL import Image, ImageTk
import threading

# Global variables
capture_active = False
video_capture = None
current_page = None
pages = {}
showed_ids = []


def show_match_dialog(user_id, image_path):
    showed_ids.append(user_id)

    dialog = tk.Toplevel()
    dialog.title("Match Found")
    
    # Load and display the user image
    user_image = Image.open(image_path)
    user_image.thumbnail((150, 150))  # Resize the image to a smaller size
    user_image = ImageTk.PhotoImage(user_image)
    
    image_label = tk.Label(dialog, image=user_image)
    image_label.pack()

    # Display the user ID
    id_label = tk.Label(dialog, text=f"User ID: {user_id}")
    id_label.pack()

    # Close button to close the dialog
    close_button = tk.Button(dialog, text="Close", command=dialog.destroy)
    close_button.pack()

    # Ensure the dialog stays on top of the main window
    dialog.grab_set()
    dialog.focus_set()
    dialog.wait_window()

def toggle_capture(video_label, result_label):
    global capture_active, video_capture
    capture_active = not capture_active
    if capture_active:
        video_capture = cv2.VideoCapture(0)
        capture_video(video_label, result_label)  # Pass the video_label as an argument

def capture_video(video_label, result_label):
    try:
        # Connect to your MySQL database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="Criminals"
        )

        if capture_active:
            while True:
                ret, frame = video_capture.read()

                # Display the video feed in the GUI
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                video_label.img = img_tk
                video_label.config(image=img_tk)
                video_label.update()

                # Encode the webcam face
                webcam_face_encoding = face_recognition.face_encodings(frame)[0]

                cursor = db.cursor()
                cursor.execute("SELECT criminal_id, criminal_image FROM criminals")
                face_data = cursor.fetchall()

                # Compare the webcam face encoding to all stored face encodings
                for user_id, stored_face in face_data:
                    load_stored_image = face_recognition.load_image_file(stored_face)
                    stored_face_encoding = face_recognition.face_encodings(load_stored_image)[0]
                    results = face_recognition.compare_faces([stored_face_encoding], webcam_face_encoding)

                    if results[0]:
                        result_label.config(text=f"Match found for user with ID {user_id}")
                        # Take appropriate action for the matched user (e.g., grant access)

                        # Display the custom dialog
                        if user_id not in showed_ids:
                            show_match_dialog(user_id, stored_face)
                        break
                    else:
                        result_label.config(text="No match found.")

                # Schedule the function to run again after a delay (in milliseconds)
                window.after(10, capture_video)
    except IndexError:
        result_label.config(text="No face found.")
        capture_video(video_label, result_label)

def create_navbar(window):
    navbar = tk.Frame(window)
    navbar.pack(fill=tk.X)

    tk.Button(navbar, text="Home", command=lambda: show_page("Home")).pack(side=tk.LEFT)
    tk.Button(navbar, text="Criminals", command=lambda: show_page("Criminals")).pack(side=tk.LEFT)
    tk.Button(navbar, text="Settings", command=lambda: show_page("Settings")).pack(side=tk.LEFT)

def show_page(name):
    global current_page
    if current_page:
        current_page.pack_forget()  # Hide the current page

    current_page = pages[name]
    current_page.pack(fill=tk.BOTH, expand=True)  # Show the selected page

def create_page(window, name):
    global pages
    page = tk.Frame(window)
    pages[name] = page

    if name == "Home":
        create_home_page(page)
    elif name == "Criminals":
        create_criminals_page(page)
    elif name == "Settings":
        create_settings_page(page)

# Function to create the Home page
def create_home_page(page):
    # Create a label to display video feed (replace with actual video display code)
    video_label = tk.Label(page, text="Video Feed Placeholder")
    video_label.pack()

    result_label = tk.Label(page, text="here the result")
    result_label.pack(expand=True, fill="both")

    capture_button = tk.Button(page, text="Start/Stop Capture", command=lambda: toggle_capture(video_label, result_label))
    capture_button.pack()

def create_criminals_page(page):
    wel = tk.Label(page, text="Welcome to the Criminals Page")
    wel.pack(expand=True, fill="both")

def create_settings_page(page):
    wel = tk.Label(page, text="Welcome to the Settings Page")
    wel.pack(expand=True, fill="both")

try:
    window = tk.Tk()
    window.geometry("800x800")
    window.title("Criminals Face Detector")

    create_navbar(window)
    create_page(window, "Home")
    create_page(window, "Criminals")
    create_page(window, "Settings")

    show_page("Home")

    window.mainloop()

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
except KeyboardInterrupt:
    pass
