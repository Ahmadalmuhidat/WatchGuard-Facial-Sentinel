import cv2
import face_recognition
import threading
import threading
import pickle
import time
import numpy
import sys
import os
import customtkinter
import DatabaseManager

from PIL import Image, ImageTk
from queue import Queue

class FaceRecognitionModal(DatabaseManager.DatabaseManager):
    def __init__(self) -> None:
        try:
            super().__init__()

            self.Cameras = []
            self.CaptureEvents = []
            self.CaptureThreads = []
            self.ShowedIDs = []
            self.Matrix = []
            self.Streams = {}

            self.ActivateCapturing = False

            self.n_frames = 5
            self.FrameCounter = 0
            self.CurrentCam = 0
            self.FacesCount = 0

            self.FramesQueue = Queue()
            self.CaptureLock = threading.Lock()

            self.connect(host="localhost", user="kali", password="kali", database="criminals")
            self.getTargets()
            self.getlogs()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def transMatrix(self, matrix):
        try:
            res = ""

            for array in matrix[0:]:
                res += "["
                for number in array:
                    res += str(number)
                res += "]"

            return res

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def listWorkingCameras(self):
        try:
            NonWorkingPorts = []
            DevPort = 0
            WorkingPorts = []
            AvailablePorts = []

            while len(NonWorkingPorts) < 6:
                camera = cv2.VideoCapture(DevPort)

                if not camera.isOpened():
                    NonWorkingPorts.append(DevPort)

                else:
                    is_reading, img = camera.read()

                    if is_reading:
                        WorkingPorts.append(DevPort)
                    else:
                        AvailablePorts.append(DevPort)

                DevPort +=1

            self.Cameras = WorkingPorts

            self.insertLog("searching for available cameras")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def startCapturing(self, CameraIndex, StopEvent):
        try:
            cap = cv2.VideoCapture(CameraIndex)
            self.Streams[CameraIndex] = cap

            while not StopEvent.is_set():
                self.captureVideo(cap)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def startAllCaptures(self):
        try:
            if not self.ActivateCapturing:
                if len(self.Cameras) > 0:
                    self.ActivateCapturing = True

                    for CameraIndex in self.Cameras:
                        self.insertLog("starting to capture streaming")

                        StopEvent = threading.Event()
                        CaptureThread = threading.Thread(target=self.startCapturing, args=(CameraIndex, StopEvent))

                        self.CaptureThreads.append(CaptureThread)
                        self.CaptureEvents.append(StopEvent)
                        
                        CaptureThread.start()
                else:
                    self.insertLog("failed to find active cameras")
            else:
                self.stopAllCaptures()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def stopAllCaptures(self) -> bool:
        try:
            if self.ActivateCapturing:
                self.ActivateCapturing = False

                for StopEvent in self.CaptureEvents:
                    StopEvent.set()

                for CaptureThread in self.CaptureThreads:
                    CaptureThread.join(timeout=5)

                self.CaptureThreads.clear()
                self.CaptureEvents.clear()

                return True
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass
    
    def getTheFace(self, frame):
        return face_recognition.face_locations(frame)
    
    def checkTargetInShowedIDs(self, targetID):
        return targetID not in self.ShowedIDs

    def AnalyzeFace(self, frame) -> bool:
        try:
            if self.FrameCounter % self.n_frames == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                face = self.getTheFace(small_frame)

                if (face):
                    self.FacesCount += 1

                    for target in self.Targets:
                        TargetID = target[0]
                        TargetFaceEncode = target[7]

                        if self.checkTargetInShowedIDs(TargetID):
                            face_encodings = face_recognition.face_encodings(small_frame, face)
                            stored_face_encoding = pickle.loads(TargetFaceEncode)

                            for face_encoding in face_encodings:
                                results = face_recognition.compare_faces([stored_face_encoding], face_encoding)

                                if results[0]:
                                    data = {
                                        'criminal_id': TargetID,
                                        'criminal_first_name': target[1],
                                        'criminal_last_name': target[2],
                                        'criminal_image': target[3],
                                        'criminal_date_of_birth': target[4],
                                        'criminal_notes': target[5],
                                        'criminal_create_date': target[6]
                                    }

                                    self.pop_match_dialog(data)

                                    self.insertLog("target with ID of {} has been detected".format(TargetID))
                else:
                    print("No face found!")

            self.FrameCounter += 1

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def displayMatrix(self, face_encodings):
        try:
            self.Matrix = numpy.array(face_encodings)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def captureVideo(self, cap):
        try:
            if self.ActivateCapturing:
                
                cap = list(self.Streams.values())[self.CurrentCam]

                while self.ActivateCapturing:
                    ret, frame = cap.read()

                    if ret:
                        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.FramesQueue.put(img_rgb)

                        thread = threading.Thread(target=self.AnalyzeFace, args=(frame,))
                        thread.start()

                    time.sleep(0.1)

        except IndexError:
            self.captureVideo()

    def pop_match_dialog(self, criminal_data):
        self.ShowedIDs.append(criminal_data['criminal_id'])

        dialog = customtkinter.CTkToplevel()
        dialog.title("Match Found")
        dialog.geometry("600x300")
        dialog.resizable(width=0, height=0)

        self.setup_dialog(dialog, criminal_data)

    def setup_dialog(self, dialog, criminal_data):
        content_frame = customtkinter.CTkFrame(dialog)
        content_frame.pack(expand=True, fill="both")

        image_frame = customtkinter.CTkFrame(content_frame, width=50, height=50)
        image_frame.pack()

        criminal_image_path = criminal_data.get('criminal_image', '')
        criminal_image = Image.open(criminal_image_path)
        criminal_image.thumbnail((150, 150))
        criminal_image = ImageTk.PhotoImage(criminal_image)

        image_label = customtkinter.CTkLabel(image_frame, image=criminal_image, text=None)
        image_label.pack()

        criminal_info_frame = customtkinter.CTkFrame(content_frame)
        criminal_info_frame.pack(padx=20, pady=20)

        headers = ["Criminal ID", "First Name", "Last Name", "Date of Birth", "Notes", "Create Date"]
        criminal_info = [criminal_data.get(key) for key in [
            'criminal_id',
            'criminal_first_name',
            'criminal_last_name',
            'criminal_date_of_birth',
            'criminal_notes',
            'criminal_create_date'
            ]]

        for col, header in enumerate(headers):
            customtkinter.CTkLabel(criminal_info_frame, text=header, padx=10, pady=5).grid(row=0, column=col, sticky="nsew")

        for col, data in enumerate(criminal_info):
            customtkinter.CTkLabel(criminal_info_frame, text=data, padx=10, pady=5).grid(row=1, column=col, sticky="nsew")

        dialog.lift()
        dialog.wait_window()


# test = FaceRecognitionModal()
# test.Database(host="localhost", user="kali", password="kali", database="criminals")
# test.getCriminals()
# test.listWorkingCameras()
# test.startAllCaptures()