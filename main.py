import tkinter as tk
import customtkinter as ctk
import os
import sys
import face_recognition
import cv2
import mysql.connector
import datetime
import shutil
import threading
import pickle
import numpy as np
import time

from PIL import Image, ImageTk
from queue import Queue

class CriminalFaceDetectorApp(tk.Tk):
    def __init__(self):
        self.capture_active = False
        self.video_capture = {}
        self.current_page = None
        self.video_label = None
        self.currentCamera = 0
        self.pages = {}
        self.showed_ids = []
        self.working_cameras = []
        self.capture_threads = []
        self.capture_events = []
        self.criminals = []
        self.matrix = []
        self.capture_lock = threading.Lock()
        self.settings = {
            "fontFamily":"",
            "fontSize": 10,
            "fontColors": "white",
            "them": "dark",
            "currentCamera": 0,
            "windowTitle": "security",
            "usePassword": False,
            "sendAlerts": False
        }

        self.Database()
        self.getCriminals()
    
    def Database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="kali",
                password="kali",
                database="criminals"
            )
            self.cursor = self.db.cursor()
        except Exception as e:
            tk.messagebox.showerror("Error", "Error occurred while connecting to the database")

    def getCriminals(self):
        self.cursor.execute("SELECT * FROM criminals")
        self.criminals = self.cursor.fetchall()

    def pop_match_dialog(self, criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date):
        self.showed_ids.append(criminal_id)

        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Match Found")
        dialog.geometry("600x300")
        dialog.resizable(width=0, height=0)

        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(expand=True, fill="both")

        image_frame = ctk.CTkFrame(content_frame, width=50, height=50)
        image_frame.pack()

        criminal_image = Image.open(criminal_image)
        criminal_image.thumbnail((150, 150))
        criminal_image = ImageTk.PhotoImage(criminal_image)

        image_label = ctk.CTkLabel(image_frame, image=criminal_image, text=None)
        image_label.pack()

        criminal_info_frame = ctk.CTkFrame(content_frame)
        criminal_info_frame.pack(padx=20, pady=20)

        headers = ["Criminal ID", "First Name", "Last Name", "Date of Birth", "Notes", "Create Date"]
        criminal_info = [criminal_id, criminal_first_name, criminal_last_name, criminal_date_of_birth, criminal_notes, criminal_create_date]

        for col, header in enumerate(headers):
            ctk.CTkLabel(criminal_info_frame, text=header, padx=10, pady=5).grid(row=0, column=col, sticky="nsew")

        for col, data in enumerate(criminal_info):
            ctk.CTkLabel(criminal_info_frame, text=data, padx=10, pady=5).grid(row=1, column=col, sticky="nsew")

        dialog.lift()
        dialog.wait_window()

    def create_navbar(self, window):
        navbar = ctk.CTkFrame(window)
        navbar.pack(fill=ctk.X)

        ctk.CTkButton(navbar, text="Home", corner_radius=0, command=lambda: self.show_page("Home")).pack(side=ctk.LEFT)
        ctk.CTkButton(navbar, text="Criminals", corner_radius=0, command=lambda: self.show_page("Criminals")).pack(side=ctk.LEFT)
        ctk.CTkButton(navbar, text="Settings", corner_radius=0, command=lambda: self.show_page("Settings")).pack(side=ctk.LEFT)
        ctk.CTkButton(navbar, text="Logs", corner_radius=0, command=lambda: self.show_page("Logs")).pack(side=ctk.LEFT)

    def show_page(self, name):
        if self.current_page:
             self.current_page.pack_forget()

        self.current_page = self.pages[name]
        self.current_page.pack(fill=ctk.BOTH, expand=True)

    def create_page(self, window, name):
        page = ctk.CTkFrame(window)
        self.pages[name] = page

        if name == "Home":
            self.create_home_page(page)
        elif name == "Criminals":
            self.create_criminals_page(page)
        elif name == "Settings":
            self.create_settings_page(page)
        elif name == "Logs":
            self.create_logs_page(page)

    def create_logs_page(self, page):
        try:
            logs_labels = []
            logs_table_frame = ctk.CTkFrame(page)
            logs_table_frame.pack(padx=10, fill="x", expand=False)

            headers = ["Log ID", "Log Date", "Log Time", "Log Event"]
            for col, header in enumerate(headers):
                header_label = ctk.CTkLabel(logs_table_frame, text=header, padx=10, pady=5)
                header_label.grid(row=0, column=col, sticky="nsew")

            for col, data in enumerate(["1", "2023-11-11", "12:00", "camera has been activted"]):
                data_label = ctk.CTkLabel(logs_table_frame, text=data, padx=10, pady=5)
                data_label.grid(row=1, column=col, sticky="nsew")
                logs_labels.append(data_label)
            
            for col, data in enumerate(["1", "2023-11-11", "06:05", "match has been found"]):
                data_label = ctk.CTkLabel(logs_table_frame, text=data, padx=10, pady=5)
                data_label.grid(row=2, column=col, sticky="nsew")
                logs_labels.append(data_label)

            # Center align the columns by setting their weights
            for col in range(len(headers)):
                logs_table_frame.columnconfigure(col, weight=1)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
    
    def transMatrix(self, matrix):
        res = ""
        for array in matrix[0:]:
            res += "["
            for number in array:
                res += str(number)
            res += "]"

        return res

    def create_home_page(self, page):
        try:
            page.rowconfigure(0, weight=1)
            page.rowconfigure(1, weight=3)
            page.rowconfigure(2, weight=1)

            page.columnconfigure(0, weight=1)
            page.columnconfigure(1, weight=3)
            page.columnconfigure(2, weight=1)

            capture_button = ctk.CTkButton(page, text="Start/Stop Capture", command=self.start_all_captures)
            capture_button.grid(row=0, column=1)

            content_frame = ctk.CTkFrame(page)
            content_frame.grid(row=1, column=1)

            content_frame.rowconfigure(0, weight=1)
            content_frame.rowconfigure(1, weight=1)

            content_frame.columnconfigure(0, weight=1)
            content_frame.columnconfigure(1, weight=3)

            self.matrix_frame = ctk.CTkFrame(content_frame, border_width=1, corner_radius=0, border_color="white", width=300, height=600)
            self.matrix_frame.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")
            self.matrix_frame.grid_propagate(False)

            result_frame = ctk.CTkFrame(content_frame, border_width=1, corner_radius=0, border_color="white", width=300, height=70)
            result_frame.grid(row=1, column=0, pady=0, padx=0, sticky="nsew")
            result_frame.grid_propagate(False)

            self.video_frame = ctk.CTkFrame(content_frame, border_width=1, corner_radius=0, border_color="white", width=600, height=700)
            self.video_frame.grid(row=0, rowspan=2, column=1, pady=0, padx=0, sticky="nsew")
            self.video_frame.grid_propagate(False)

            result_text = ctk.CTkLabel(result_frame, text="Number of detected faces is: 0", bg_color="transparent", font=ctk.CTkFont(size=15))
            result_text.pack(padx=5, pady=15)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def create_criminals_page(self, page):
        try:
            add_criminal_frame = ctk.CTkFrame(page)
            add_criminal_frame.pack(padx=20, pady=20)

            criminal_id_label = ctk.CTkLabel(add_criminal_frame, text="Criminal ID:")
            criminal_id_label.grid(row=0, column=0, padx=10, pady=5)
            criminal_id_entry = ctk.CTkEntry(add_criminal_frame)
            criminal_id_entry.grid(row=0, column=1, padx=10, pady=5)

            criminal_first_name_label = ctk.CTkLabel(add_criminal_frame, text="First Name:")
            criminal_first_name_label.grid(row=1, column=0, padx=10, pady=5)
            criminal_first_name_entry = ctk.CTkEntry(add_criminal_frame)
            criminal_first_name_entry.grid(row=1, column=1, padx=10, pady=5)

            criminal_last_name_label = ctk.CTkLabel(add_criminal_frame, text="Last Name:")
            criminal_last_name_label.grid(row=2, column=0, padx=10, pady=5)
            criminal_last_name_entry = ctk.CTkEntry(add_criminal_frame)
            criminal_last_name_entry.grid(row=2, column=1, padx=10, pady=5)

            criminal_dob_label = ctk.CTkLabel(add_criminal_frame, text="Date of Birth:")
            criminal_dob_label.grid(row=3, column=0, padx=10, pady=5)
            criminal_dob_entry = ctk.CTkEntry(add_criminal_frame)
            criminal_dob_entry.grid(row=3, column=1, padx=10, pady=5)

            criminal_notes_label = ctk.CTkLabel(add_criminal_frame, text="Notes:")
            criminal_notes_label.grid(row=4, column=0, padx=10, pady=5)
            criminal_notes_entry = ctk.CTkEntry(add_criminal_frame, placeholder_text="optional")
            criminal_notes_entry.grid(row=4, column=1, padx=10, pady=5)

            criminal_image_entry = ctk.CTkEntry(add_criminal_frame)
            criminal_image_entry.grid(row=5, column=1, padx=10, pady=5)

            search_bar_frame = ctk.CTkFrame(page, bg_color="transparent")
            search_bar_frame.pack(padx=10, fill="x", expand=False)

            search_button = ctk.CTkButton(search_bar_frame, text="Search", command=lambda: searchCriminals(search_bar.get()))
            search_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=5)

            search_bar = ctk.CTkEntry(search_bar_frame, width=400, placeholder_text="Search for criminals...")
            search_bar.grid(row=0, column=1, sticky="nsew", pady=10)

            delete_button = ctk.CTkButton(search_bar_frame, width=100, text="Delete", command=lambda: deleteCriminal(delete_bar.get()))
            delete_button.grid(row=0, column=2, sticky="nsew", pady=10, padx=5)

            delete_bar = ctk.CTkEntry(search_bar_frame, width=100, placeholder_text="ID")
            delete_bar.grid(row=0, column=3, sticky="nsew", pady=10)

            reset_button = ctk.CTkButton(search_bar_frame, width=100, text="Reset", command=lambda: reset())
            reset_button.grid(row=0, column=4, sticky="nsew", pady=10, padx=5)

            criminals_labels = []
            criminals_table_frame = ctk.CTkFrame(page)
            criminals_table_frame.pack(padx=10, fill="x", expand=False)

            headers = ["Criminal ID", "First Name", "Last Name", "Date of Birth", "Notes", "Image", "Create Date"]
            for col, header in enumerate(headers):
                header_label = ctk.CTkLabel(criminals_table_frame, text=header, padx=10, pady=5)
                header_label.grid(row=0, column=col, sticky="nsew")

            def searchCriminals(id):
                for label in criminals_labels:
                    label.destroy()

                query = "SELECT * FROM criminals WHERE criminal_id=" + id
                self.cursor.execute(query)
                criminals = self.cursor.fetchall()

                for row, criminal in enumerate(criminals, start=1):
                    criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date = criminal
                    criminal_data = [criminal_id, criminal_first_name, criminal_last_name, criminal_date_of_birth, criminal_notes, criminal_image, criminal_create_date]

                    for col, data in enumerate(criminal_data):
                        data_label = ctk.CTkLabel(criminals_table_frame, text=data, padx=10, pady=5)
                        data_label.grid(row=row, column=col, sticky="nsew")
                        criminals_labels.append(data_label)

                for col in range(len(criminal_data)):
                    criminals_table_frame.columnconfigure(col, weight=1)

            def deleteCriminal(id):
                query = "DELETE FROM criminals WHERE criminal_id=" + id
                self.cursor.execute(query)
                self.db.commit()

                # delete the image from criminals

                displayExistingCriminals()
            
            def displayExistingCriminals():
                try:
                    for label in criminals_labels:
                        label.destroy()

                    self.cursor.execute("SELECT * FROM criminals")
                    criminals = self.cursor.fetchall()

                    if len(criminals) > 0:
                        for row, criminal in enumerate(criminals, start=1):
                            criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date, criminal_face_encode = criminal
                            criminal_data = [criminal_id, criminal_first_name, criminal_last_name, criminal_date_of_birth, criminal_notes, criminal_image, criminal_create_date]

                            for col, data in enumerate(criminal_data):
                                data_label = ctk.CTkLabel(criminals_table_frame, text=data, padx=10, pady=5)
                                data_label.grid(row=row, column=col, sticky="nsew")
                                criminals_labels.append(data_label)

                        # Center align the columns by setting their weights
                        for col in range(len(criminal_data)):
                            criminals_table_frame.columnconfigure(col, weight=1)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc_obj)

            def reset():
                displayExistingCriminals()

            def upload_image():
                try:
                    file_path = tk.filedialog.askopenfilename()
                    if file_path:
                        image = Image.open(file_path)
                        image.thumbnail((150, 150))
                        self.image_path = file_path
                        criminal_image_entry.delete(0, ctk.END)
                        criminal_image_entry.insert(0, file_path)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc_obj)
            
            def validateEntries():
                try:
                    if not criminal_id_entry.get():
                        tk.messagebox.showerror("Missing Entry", "please enter criminal ID")
                        return False
                    elif not criminal_first_name_entry.get():
                        tk.messagebox.showerror("Missing Entry", "please enter criminal first name")
                        return False
                    elif not criminal_last_name_entry.get():
                        tk.messagebox.showerror("Missing Entry", "please enter criminal last name")
                        return False
                    elif not criminal_dob_entry.get():
                        tk.messagebox.showerror("Missing Entry", "please enter criminal date of birth")
                        return False
                    elif not criminal_image_entry.get():
                        tk.messagebox.showerror("Missing Entry", "please select criminal image")
                        return False

                    return True

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc_obj)

            def save_criminal():
                try:
                    if validateEntries():
                        if self.image_path and os.path.exists(self.image_path):
                            image_filename = os.path.basename(self.image_path)
                            destination_path = os.path.join("criminals", image_filename)
                            shutil.copyfile(self.image_path, destination_path)

                        load_stored_image = face_recognition.load_image_file(self.image_path)
                        stored_face_encoding = np.array(face_recognition.face_encodings(load_stored_image)[0])
                        serialized_encoding = pickle.dumps(stored_face_encoding)
                        
                        query = "INSERT INTO criminals (criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date, criminal_face_encode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        data = (
                            criminal_id_entry.get(),
                            criminal_first_name_entry.get(),
                            criminal_last_name_entry.get(),
                            destination_path if hasattr(self, "image_path") else "",
                            criminal_dob_entry.get(),
                            criminal_notes_entry.get(),
                            datetime.date.today(),
                            serialized_encoding
                        )
                        self.cursor.execute(query, data)
                        self.db.commit()

                        criminal_id_entry.delete(0, ctk.END)
                        criminal_first_name_entry.delete(0, ctk.END)
                        criminal_last_name_entry.delete(0, ctk.END)
                        criminal_dob_entry.delete(0, ctk.END)
                        criminal_notes_entry.delete(0, ctk.END)
                        criminal_image_entry.delete(0, ctk.END)

                        displayExistingCriminals()
                    else:
                        return

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc_obj)
            
            displayExistingCriminals()

            upload_button = ctk.CTkButton(add_criminal_frame, text="Upload Image", width=30, height=30, command=upload_image)
            upload_button.grid(row=5, column=0, pady=5)

            save_button = ctk.CTkButton(add_criminal_frame, text="Save Criminal", command=save_criminal)
            save_button.grid(row=7, columnspan=2, pady=5, sticky="nsew")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def list_working_cameras(self):
        non_working_ports = []
        dev_port = 0
        working_ports = []
        available_ports = []

        while len(non_working_ports) < 6:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                # print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    # print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(dev_port)
                else:
                    # print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
            dev_port +=1

        return available_ports, working_ports, non_working_ports

    def create_settings_page(self, page):
        try:
            page.rowconfigure(0, weight=1)
            page.rowconfigure(1, weight=1)
            page.rowconfigure(2, weight=1)

            page.columnconfigure(0, weight=1)
            page.columnconfigure(1, weight=3)
            page.columnconfigure(2, weight=1)

            fontFrame = ctk.CTkFrame(page, border_color="white", border_width=2)
            fontFrame.grid(row=0, column=1, pady=10, sticky="nsew")

            ctk.CTkLabel(fontFrame, text="Font Family:").pack()
            font_family_entry = ctk.CTkEntry(fontFrame, width=200)
            font_family_entry.insert(0, "")
            font_family_entry.pack()

            ctk.CTkLabel(fontFrame, text="Font Size:").pack()
            font_size_entry = ctk.CTkEntry(fontFrame, width=200)
            font_size_entry.insert(0, "10")
            font_size_entry.pack()

            ctk.CTkLabel(fontFrame, text="Font Color:").pack()
            font_color_entry = ctk.CTkEntry(fontFrame, width=200)
            font_color_entry.insert(0, "white")
            font_color_entry.pack()

            generalFrame = ctk.CTkFrame(page, border_color="white", border_width=2)
            generalFrame.grid(row=1, column=1, pady=10, sticky="nsew")

            settings_label = ctk.CTkLabel(generalFrame, text="Active Cameras")
            settings_label.pack()

            self.working_cameras = self.list_working_cameras()[1]

            if len(self.working_cameras) > 0:
                camera_combobox = ctk.CTkComboBox(generalFrame, values=[str(x) for x in self.working_cameras], width=200)
                camera_combobox.set(self.working_cameras[0])
                camera_combobox.pack()
            else:
                settings_label.configure(text="No active cameras found")

            ctk.CTkLabel(generalFrame, text="Window Title:").pack()
            window_title_entry = ctk.CTkEntry(generalFrame, width=200)
            window_title_entry.insert(0, "security")
            window_title_entry.pack()

            use_password_checkbox = ctk.CTkCheckBox(generalFrame, text="Use Password").pack(pady=10)
            send_alerts_checkbox = ctk.CTkCheckBox(generalFrame, text="Send Alerts").pack(pady=10)

            ctk.CTkLabel(generalFrame, text="Theme:").pack()
            theme_entry = ctk.CTkComboBox(generalFrame, values=["dark", "light"], width=200)
            theme_entry.set("dark")
            theme_entry.pack()

            def save_settings():
                self.settings["fontFamily"] = font_family_entry.get()
                self.settings["fontSize"] = int(font_size_entry.get())
                self.settings["fontColor"] = font_color_entry.get()
                self.settings["theme"] = theme_entry.get()
                self.settings["currentCamera"] = camera_combobox.get()
                self.settings["windowTitle"] = window_title_entry.get()
                self.settings["usePassword"] = use_password_checkbox
                self.settings["sendAlerts"] = send_alerts_checkbox

            save_button = ctk.CTkButton(page, text="Save", width=400, command=save_settings)
            save_button.grid(row=2, column=1, pady=10, sticky="n")
    
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)    

    def start_capture(self, camera_index, stop_event):
        cap = cv2.VideoCapture(camera_index)
        self.video_capture[camera_index] = cap

        while not stop_event.is_set():
            self.capture_video(cap)

    def start_all_captures(self):
        if not self.capture_active:
            if len(self.working_cameras) > 0:
                self.capture_active = True

                for camera_index in self.working_cameras:
                    stop_event = threading.Event()
                    capture_thread = threading.Thread(target=self.start_capture, args=(camera_index, stop_event))

                    self.capture_threads.append(capture_thread)
                    self.capture_events.append(stop_event)
                    
                    capture_thread.start()
            else:
                tk.messagebox.showerror("Error", "No Active Cameras Found")
        else:
            self.stop_all_captures()

    def stop_all_captures(self):
        if self.capture_active:
            self.capture_active = False

            for stop_event in self.capture_events:
                stop_event.set()

            for capture_thread in self.capture_threads:
                capture_thread.join(timeout=5)

            self.capture_threads = []
            self.capture_events = []

    def capture_video(self, cap):
            try:
                if self.capture_active:
                    if self.video_label is None:
                        self.video_label = ctk.CTkLabel(self.video_frame, text=None)
                        self.video_label.pack(padx=5, pady=15)

                    n_frames = 5
                    self.frame_counter = 0
                    frame_queue = Queue()

                    def displayMatrix(face_encodings): 
                        webcam_face_encoding = np.array(face_encodings)

                        for i in range(16):
                            for j in range(8):
                                index = i * 8 + j
                                if index < len(webcam_face_encoding):
                                    label = ctk.CTkLabel(self.matrix_frame, text=str(webcam_face_encoding[index]), bg_color="transparent", font=ctk.CTkFont(size=10), width=10, height=3, wraplength=100, anchor="center")
                                    label.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
            
                    def AnalyzeFace(frame):
                        if self.frame_counter % n_frames == 0:
                            # Reduce the frame size for faster processing (adjust as needed)
                            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                            for criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date, criminal_face_encode in self.criminals:
                                if criminal_id not in self.showed_ids:
                                    face_locations = face_recognition.face_locations(small_frame)
                                    face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                                    stored_face_encoding = pickle.loads(criminal_face_encode)

                                    # thread = threading.Thread(target=displayMatrix, args=(face_encodings,))
                                    # thread.start()

                                    for face_encoding in face_encodings:
                                        results = face_recognition.compare_faces([stored_face_encoding], face_encoding)

                                        if results[0]:
                                            self.pop_match_dialog(criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date)
                                        break
                        self.frame_counter += 1
                    
                    cap = list(self.video_capture.values())[self.currentCamera]

                    while self.capture_active:
                        ret, frame = cap.read()

                        if ret:
                            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame_queue.put(img_rgb)

                            img_rgb = frame_queue.get(block=False)
                            img = Image.fromarray(img_rgb)
                            img_tk = ImageTk.PhotoImage(image=img)
                            
                            with self.capture_lock:
                                self.video_label.img_tk = img_tk
                                self.video_label.configure(image=img_tk)

                            thread = threading.Thread(target=AnalyzeFace, args=(frame,))
                            thread.start()

                        time.sleep(0.1)  # Adjust the sleep duration to control the frame rate

            except IndexError:
                self.capture_video()

    def run(self):
        try:
            self.window = ctk.CTk()
            self.window.geometry("1100x950")
            self.window.resizable(width=0, height=0)
            self.window.title("Criminals Face Detector")

            self.create_navbar(self.window)
            self.create_page(self.window, "Home")
            self.create_page(self.window, "Criminals")
            self.create_page(self.window, "Settings")
            self.create_page(self.window, "Logs")

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
