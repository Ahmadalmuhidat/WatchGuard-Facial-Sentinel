import tkinter as tk
import customtkinter
import os
import sys
import datetime
import FaceRecognitionModal
import threading

from PIL import Image

class UserInterface(FaceRecognitionModal.FaceRecognitionModal):
    def __init__(self):
        super(UserInterface, self).__init__()

        self.CurrentPage = None
        self.VideoLabel = None
        self.ImagePath = None

        self.pages = {}
        self.ShowedIDs = []
        self.CriminalsLabels = []
        self.LogsLabels = []
        self.VideoCapture = {}

        self.Settings = {
            "fontFamily":"",
            "fontSize": 10,
            "fontColors": "white",
            "them": "dark",
            "currentCamera": 0,
            "windowTitle": "security",
            "usePassword": False,
            "sendAlerts": False
        }

    def Navbar(self, window):
        navbar = customtkinter.CTkFrame(window)
        navbar.pack(fill=customtkinter.X)

        HomeButton = customtkinter.CTkButton(navbar, text="Home")
        HomeButton.configure(corner_radius=0, command=lambda: self.showPage("Home"))
        HomeButton.pack(side=customtkinter.LEFT)

        CriminalsButton = customtkinter.CTkButton(navbar, text="Criminals")
        CriminalsButton.configure(corner_radius=0, command=lambda: self.showPage("Criminals"))
        CriminalsButton.pack(side=customtkinter.LEFT)

        SettingsButton = customtkinter.CTkButton(navbar, text="Settings")
        SettingsButton.configure(corner_radius=0, command=lambda: self.showPage("Settings"))
        SettingsButton.pack(side=customtkinter.LEFT)

        LogsButton = customtkinter.CTkButton(navbar, text="Logs")
        LogsButton.configure(corner_radius=0, command=lambda: self.showPage("Logs"))
        LogsButton.pack(side=customtkinter.LEFT)

    def showPage(self, name):
        if self.CurrentPage:
             self.CurrentPage.pack_forget()

        self.CurrentPage = self.pages[name]
        self.CurrentPage.pack(fill=customtkinter.BOTH, expand=True)

    def createPage(self, window, name):
        page = customtkinter.CTkFrame(window)
        self.pages[name] = page

        if name == "Home":
            self.createHomePage(page)
        elif name == "Criminals":
            self.createCriminalsPage(page)
        elif name == "Settings":
            self.createSettingsPage(page)
        elif name == "Logs":
            self.createLogsPage(page)

    def createLogsPage(self, page):
        try:
            def updateLogs(term):
                self.searchLogs(term)
                displayLogsTable()
            
            def resetAllInputs():
                self.getlogs()
                displayLogsTable()
            
            def displayLogsTable():
                for label in self.LogsLabels:
                    label.destroy()

                if len(self.Logs) > 0:
                    for row, log in enumerate(self.Logs, start=1):
                        log_id, log_date, log_time, log_event = log
                        log_data = [log_id, log_date, log_time, log_event]

                        for col, data in enumerate(log_data):
                            data_label = customtkinter.CTkLabel(logs_table_frame, text=data, padx=10, pady=5)
                            data_label.grid(row=row, column=col, sticky="nsew")
                            self.LogsLabels.append(data_label)

                for col in range(len(headers)):
                    logs_table_frame.columnconfigure(col, weight=1)
                
                results_count.configure(text="Results: " + str(len(self.LogsLabels)))

            search_bar_frame = customtkinter.CTkFrame(page, bg_color="transparent")
            search_bar_frame.pack(padx=10, fill="x", expand=False)

            search_button = customtkinter.CTkButton(search_bar_frame, text="Search", command=lambda: updateLogs(search_bar.get()))
            search_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=5)

            search_bar = customtkinter.CTkEntry(search_bar_frame, width=400, placeholder_text="Search for logs")
            search_bar.grid(row=0, column=1, sticky="nsew", pady=10)

            reset_button = customtkinter.CTkButton(search_bar_frame, text="Reset", command=resetAllInputs)
            reset_button.grid(row=0, column=2, sticky="nsew", pady=10, padx=5)

            results_count = customtkinter.CTkLabel(search_bar_frame)
            results_count.grid(row=0, column=3, padx=10, pady=5)

            logs_table_frame = customtkinter.CTkScrollableFrame(page)
            logs_table_frame.pack(padx=10, fill="both", expand=True)

            headers = ["Log ID", "Log Date", "Log Time", "Log Event"]
            for col, header in enumerate(headers):
                header_label = customtkinter.CTkLabel(logs_table_frame, text=header, padx=10, pady=5)
                header_label.grid(row=0, column=col, sticky="nsew")

            displayLogsTable()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def createHomePage(self, page):
        try:
            page.rowconfigure(0, weight=1)
            page.rowconfigure(1, weight=3)
            page.rowconfigure(2, weight=1)

            page.columnconfigure(0, weight=1)
            page.columnconfigure(1, weight=3)
            page.columnconfigure(2, weight=1)

            content_frame = customtkinter.CTkFrame(page)
            content_frame.grid(row=1, column=1, sticky="new")
            content_frame.rowconfigure(0, weight=1)
            content_frame.rowconfigure(1, weight=1)
            content_frame.columnconfigure(0, weight=1)
            content_frame.columnconfigure(1, weight=1)
            content_frame.columnconfigure(2, weight=1)
            content_frame.columnconfigure(3, weight=1)

            # Cameras count frame
            capture_button = customtkinter.CTkButton(content_frame, font=customtkinter.CTkFont(size=20))
            capture_button.grid(row=0, column=0, columnspan=2, sticky="nswe", pady=20)
            capture_button.configure(text="Start Capture", command=self.startAllCaptures)

            StopCaptureButton = customtkinter.CTkButton(content_frame, font=customtkinter.CTkFont(size=20))
            StopCaptureButton.grid(row=0, column=2, columnspan=2, sticky="nswe", pady=20)
            StopCaptureButton.configure(text="Stop Capture", command=self.stopAllCaptures, height=50, fg_color="red")

            cameras_count_frame = customtkinter.CTkFrame(content_frame)
            cameras_count_frame.grid(row=1, column=0, sticky="nsew")
            cameras_count_frame.grid_propagate(False)

            self.cameras_count = customtkinter.CTkLabel(cameras_count_frame)
            self.cameras_count.pack(padx=5, pady=15)
            self.cameras_count.configure(text="Cameras Count \n\n0", bg_color="transparent", font=customtkinter.CTkFont(size=20))

            faces_count_frame = customtkinter.CTkFrame(content_frame, border_width=1)
            faces_count_frame.grid(row=1, column=1, sticky="nsew")
            faces_count_frame.grid_propagate(False)

            self.faces_count = customtkinter.CTkLabel(faces_count_frame)
            self.faces_count.pack(padx=5, pady=15)
            self.faces_count.configure(text="Faces Count \n\n0", bg_color="transparent", font=customtkinter.CTkFont(size=20))

            users_count_frame = customtkinter.CTkFrame(content_frame)
            users_count_frame.grid(row=1, column=2, sticky="nsew")
            users_count_frame.grid_propagate(False)

            self.users_count = customtkinter.CTkLabel(users_count_frame)
            self.users_count.pack(padx=5, pady=15)
            self.users_count.configure(text="Users Count \n\n0", bg_color="transparent", font=customtkinter.CTkFont(size=20))

            CPU_count_frame = customtkinter.CTkFrame(content_frame)
            CPU_count_frame.grid(row=1, column=3, sticky="nsew")
            CPU_count_frame.grid_propagate(False)

            self.CPU_count = customtkinter.CTkLabel(CPU_count_frame)
            self.CPU_count.pack(padx=5, pady=15)
            self.CPU_count.configure(text="CPU Usage \n\n0", bg_color="transparent", font=customtkinter.CTkFont(size=20))

            cams_table_frame = customtkinter.CTkFrame(content_frame)

            if len(self.Cameras) > 3:
                cams_table_frame = customtkinter.CTkScrollableFrame(content_frame)

            cams_table_frame.grid(row=2, column=0, columnspan=4, sticky="nswe")

            CamsLabels = []

            headers = ["Cam", "header 2", "header 3", "Action"]
            for col, header in enumerate(headers):
                header_label = customtkinter.CTkLabel(cams_table_frame, text=header, padx=10, pady=5, font=customtkinter.CTkFont(size=20))
                header_label.grid(row=0, column=col, sticky="nsew")

            def showCamsTable():
                for label in CamsLabels:
                    label.destroy()

                if len(self.Targets) > 0:
                    for index, cam in enumerate(self.Cameras, start=1):
                        cam_data = [index, "info 2", "info 3"]

                        for col, data in enumerate(cam_data):
                            data_label = customtkinter.CTkLabel(cams_table_frame, text=data, padx=10, pady=5)
                            data_label.grid(row=index, column=col, sticky="nsew")
                            CamsLabels.append(data_label)
                            view_button = customtkinter.CTkButton(cams_table_frame, font=customtkinter.CTkFont(size=20))
                            view_button.grid(row=index, column=col + 1, sticky="nsew")
                            view_button.configure(text="View", command=lambda: self.showVideoFrame(index))

                for col in range(len(headers)):
                    cams_table_frame.columnconfigure(col, weight=1)

            showCamsTable()
            # threading.Thread(target=self.updateVideoFrame).start()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def createCriminalsPage(self, page):
        try:
            def searchCriminals(term):
                self.searchTarget(term)
                displayTargetsTable()

            def deleteCriminal(term):
                self.removeTarget(term)
                self.getTargets()
                displayTargetsTable()
            
            def displayTargetsTable():
                for label in self.CriminalsLabels:
                    label.destroy()

                if len(self.Targets) > 0:
                    for row, criminal in enumerate(self.Targets, start=1):
                        criminal_id, criminal_first_name, criminal_last_name, criminal_image, criminal_date_of_birth, criminal_notes, criminal_create_date, criminal_face_encode = criminal
                        criminal_data = [criminal_id, criminal_first_name, criminal_last_name, criminal_date_of_birth, criminal_notes, criminal_image, criminal_create_date]

                        for col, data in enumerate(criminal_data):
                            data_label = customtkinter.CTkLabel(criminals_table_frame, text=data, padx=10, pady=5)
                            data_label.grid(row=row, column=col, sticky="nsew")
                            self.CriminalsLabels.append(data_label)

                for col in range(len(headers)):
                    criminals_table_frame.columnconfigure(col, weight=1)
                
                results_count.configure(text="Results: " + str(len(self.CriminalsLabels)))

            def resetAllInputs():
                self.getTargets()
                displayTargetsTable()

            def uploadImage():
                FilePath = tk.filedialog.askopenfilename()
                if FilePath:
                    image = Image.open(FilePath)
                    image.thumbnail((150, 150))
                    self.ImagePath = FilePath
                    criminal_image_entry.delete(0, customtkinter.END)
                    criminal_image_entry.insert(0, FilePath)

            def saveCriminal():
                ID = criminal_id_entry.get()
                FirstName = criminal_first_name_entry.get()
                LastName = criminal_last_name_entry.get()
                DateOfBirth = criminal_dob_entry.get()
                Notes = criminal_notes_entry.get()
                TodayDate = datetime.date.today()

                if self.validateTargetEntries(ID, FirstName, LastName, DateOfBirth, self.ImagePath):
                    self.insertTarget(
                        ID = ID,
                        FirstName = FirstName,
                        LastName = LastName,
                        ImagePath =  self.ImagePath,
                        DateOfBirth = DateOfBirth,
                        Notes = Notes,
                        TodayDate = TodayDate
                    )

                    # clear inputs
                    criminal_id_entry.delete(0, customtkinter.END)
                    criminal_first_name_entry.delete(0, customtkinter.END)
                    criminal_last_name_entry.delete(0, customtkinter.END)
                    criminal_dob_entry.delete(0, customtkinter.END)
                    criminal_notes_entry.delete(0, customtkinter.END)
                    criminal_image_entry.delete(0, customtkinter.END)

                    resetAllInputs()

            add_criminal_frame = customtkinter.CTkFrame(page)
            add_criminal_frame.pack(padx=20, pady=20)

            criminal_id_label = customtkinter.CTkLabel(add_criminal_frame, text="Criminal ID:")
            criminal_id_label.grid(row=0, column=0, padx=10, pady=5)
            criminal_id_entry = customtkinter.CTkEntry(add_criminal_frame)
            criminal_id_entry.grid(row=0, column=1, padx=10, pady=5)

            criminal_first_name_label = customtkinter.CTkLabel(add_criminal_frame, text="First Name:")
            criminal_first_name_label.grid(row=1, column=0, padx=10, pady=5)
            criminal_first_name_entry = customtkinter.CTkEntry(add_criminal_frame)
            criminal_first_name_entry.grid(row=1, column=1, padx=10, pady=5)

            criminal_last_name_label = customtkinter.CTkLabel(add_criminal_frame, text="Last Name:")
            criminal_last_name_label.grid(row=2, column=0, padx=10, pady=5)
            criminal_last_name_entry = customtkinter.CTkEntry(add_criminal_frame)
            criminal_last_name_entry.grid(row=2, column=1, padx=10, pady=5)

            criminal_dob_label = customtkinter.CTkLabel(add_criminal_frame, text="Date of Birth:")
            criminal_dob_label.grid(row=3, column=0, padx=10, pady=5)
            criminal_dob_entry = customtkinter.CTkEntry(add_criminal_frame, placeholder_text="YYYY-MM-DD")
            criminal_dob_entry.grid(row=3, column=1, padx=10, pady=5)

            criminal_notes_label = customtkinter.CTkLabel(add_criminal_frame, text="Notes:")
            criminal_notes_label.grid(row=4, column=0, padx=10, pady=5)
            criminal_notes_entry = customtkinter.CTkEntry(add_criminal_frame, placeholder_text="optional")
            criminal_notes_entry.grid(row=4, column=1, padx=10, pady=5)

            criminal_image_entry = customtkinter.CTkEntry(add_criminal_frame)
            criminal_image_entry.grid(row=5, column=1, padx=10, pady=5)

            search_bar_frame = customtkinter.CTkFrame(page, bg_color="transparent")
            search_bar_frame.pack(padx=10, fill="x", expand=False)

            search_button = customtkinter.CTkButton(search_bar_frame, text="Search")
            search_button.grid(row=0, column=0, sticky="nsew", pady=10, padx=5)
            search_button.configure(command=lambda: searchCriminals(search_bar.get()))

            search_bar = customtkinter.CTkEntry(search_bar_frame, width=400, placeholder_text="Search for criminals...")
            search_bar.grid(row=0, column=1, sticky="nsew", pady=10)

            delete_button = customtkinter.CTkButton(search_bar_frame, width=100, text="Delete")
            delete_button.grid(row=0, column=2, sticky="nsew", pady=10, padx=5)
            delete_button.configure(command=lambda: deleteCriminal(delete_bar.get()))

            delete_bar = customtkinter.CTkEntry(search_bar_frame, width=100, placeholder_text="ID")
            delete_bar.grid(row=0, column=3, sticky="nsew", pady=10)

            reset_button = customtkinter.CTkButton(search_bar_frame, width=100, text="Reset")
            reset_button.grid(row=0, column=4, sticky="nsew", pady=10, padx=5)
            reset_button.configure(command=resetAllInputs)

            results_count = customtkinter.CTkLabel(search_bar_frame)
            results_count.grid(row=0, column=5, padx=10, pady=5)

            criminals_table_frame = customtkinter.CTkFrame(page)
            criminals_table_frame.pack(padx=10, fill="x", expand=False)

            headers = ["Criminal ID", "First Name", "Last Name", "Date of Birth", "Notes", "Image", "Create Date"]
            for col, header in enumerate(headers):
                header_label = customtkinter.CTkLabel(criminals_table_frame, text=header, padx=10, pady=5)
                header_label.grid(row=0, column=col, sticky="nsew")

            displayTargetsTable()

            upload_button = customtkinter.CTkButton(add_criminal_frame)
            upload_button.grid(row=5, column=0, pady=5)
            upload_button.configure(text="Upload Image", width=30, height=30, command=uploadImage)

            save_button = customtkinter.CTkButton(add_criminal_frame)
            save_button.grid(row=7, columnspan=2, pady=5, sticky="nsew")
            save_button.configure(text="Save Criminal", command=saveCriminal)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def createSettingsPage(self, page):
        try:
            page.rowconfigure(0, weight=1)
            page.rowconfigure(1, weight=1)
            page.rowconfigure(2, weight=1)

            page.columnconfigure(0, weight=1)
            page.columnconfigure(1, weight=3)
            page.columnconfigure(2, weight=1)

            fontFrame = customtkinter.CTkFrame(page, border_color="white", border_width=2)
            fontFrame.grid(row=0, column=1, pady=10, sticky="nsew")

            customtkinter.CTkLabel(fontFrame, text="Font Family:").pack()
            font_family_entry = customtkinter.CTkEntry(fontFrame, width=200)
            font_family_entry.insert(0, "")
            font_family_entry.pack()

            customtkinter.CTkLabel(fontFrame, text="Font Size:").pack()
            font_size_entry = customtkinter.CTkEntry(fontFrame, width=200)
            font_size_entry.insert(0, "10")
            font_size_entry.pack()

            customtkinter.CTkLabel(fontFrame, text="Font Color:").pack()
            font_color_entry = customtkinter.CTkEntry(fontFrame, width=200)
            font_color_entry.insert(0, "white")
            font_color_entry.pack()

            generalFrame = customtkinter.CTkFrame(page, border_color="white", border_width=2)
            generalFrame.grid(row=1, column=1, pady=10, sticky="nsew")

            settings_label = customtkinter.CTkLabel(generalFrame, text="Active Cameras")
            settings_label.pack()

            if len(self.Cameras) > 0:
                camera_combobox = customtkinter.CTkComboBox(generalFrame, values=[str(x) for x in self.Cameras], width=200)
                camera_combobox.set(self.Cameras[0])
                camera_combobox.pack()
            else:
                settings_label.configure(text="No active cameras found")

            customtkinter.CTkLabel(generalFrame, text="Window Title:").pack()
            window_title_entry = customtkinter.CTkEntry(generalFrame, width=200)
            window_title_entry.insert(0, "security")
            window_title_entry.pack()

            use_password_checkbox = customtkinter.CTkCheckBox(generalFrame, text="Use Password").pack(pady=10)
            send_alerts_checkbox = customtkinter.CTkCheckBox(generalFrame, text="Send Alerts").pack(pady=10)

            customtkinter.CTkLabel(generalFrame, text="Theme:").pack()
            theme_entry = customtkinter.CTkComboBox(generalFrame, values=["dark", "light"], width=200)
            theme_entry.set("dark")
            theme_entry.pack()

            def save_settings():
                self.Settings["fontFamily"] = font_family_entry.get()
                self.Settings["fontSize"] = int(font_size_entry.get())
                self.Settings["fontColor"] = font_color_entry.get()
                self.Settings["theme"] = theme_entry.get()
                self.Settings["currentCamera"] = camera_combobox.get()
                self.Settings["windowTitle"] = window_title_entry.get()
                self.Settings["usePassword"] = use_password_checkbox
                self.Settings["sendAlerts"] = send_alerts_checkbox

            save_button = customtkinter.CTkButton(page, text="Save", width=400, command=save_settings)
            save_button.grid(row=2, column=1, pady=10, sticky="n")
    
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)    

    def run(self):
        try:
            self.window = customtkinter.CTk()
            self.window.geometry("1100x950")
            self.window.resizable(width=0, height=0)
            self.window.title("Criminals Face Detector")

            self.Navbar(self.window)
            self.createPage(self.window, "Home")
            self.createPage(self.window, "Criminals")
            self.createPage(self.window, "Settings")
            self.createPage(self.window, "Logs")

            self.showPage("Home")

            threading.Thread(target=self.updateCPUMetrics).start()
            threading.Thread(target=self.updateCamerasCount).start()
            threading.Thread(target=self.updateFacesCount).start()

            self.window.mainloop()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
        except KeyboardInterrupt:
            pass

CriminalFaceDetector = UserInterface()
CriminalFaceDetector.run()