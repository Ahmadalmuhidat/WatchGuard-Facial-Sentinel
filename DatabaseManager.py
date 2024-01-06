import mysql.connector
import sys
import os
import uuid
import shutil
import tkinter
import face_recognition
import pickle
import numpy
import re

from datetime import datetime, date

class DatabaseManager:
    def __init__(self) -> None:
        try:
            self.Targets = []
            self.Logs = []

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def connect(self, host, user, password, database):
        try:
            self.db = mysql.connector.connect(
                host = host,
                user = user,
                password = password,
                database = database
            )

            self.cursor = self.db.cursor()

            self.insertLog("connected to database")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass
    
    def validateTargetEntries(self, ID, FirstName, LastName, DateOfBirth, ImagePath):
        try:
            if not ID:
                tkinter.messagebox.showerror("Missing Entry", "please enter criminal ID")
                return False
            elif not FirstName:
                tkinter.messagebox.showerror("Missing Entry", "please enter criminal first name")
                return False
            elif not LastName:
                tkinter.messagebox.showerror("Missing Entry", "please enter criminal last name")
                return False
            elif not DateOfBirth:
                tkinter.messagebox.showerror("Missing Entry", "please enter criminal date of birth")
                return False
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", DateOfBirth):
                tkinter.messagebox.showerror("Wrong Date Format", "the allowed date format is YYYY-MM-DD")
                return False
            elif not ImagePath:
                tkinter.messagebox.showerror("Missing Entry", "please select criminal image")
                return False
            elif not os.path.exists(ImagePath):
                tkinter.messagebox.showerror("Inavlid Path", "the selected path is not valid")
                return False
            elif not self.checkFaceInImage(ImagePath):
                tkinter.messagebox.showerror("Face Not Found", "the uploaded image contains no face")
                return False

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def getFaceEncoding(self, path):
        try:
            load_stored_image = face_recognition.load_image_file(path)
            stored_face_encoding = numpy.array(face_recognition.face_encodings(load_stored_image)[0])
            return pickle.dumps(stored_face_encoding)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def checkFaceInImage(self, path):
        try:
            FaceFound = face_recognition.face_locations(path)

            if FaceFound:
                return True
            else:
                return False

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def insertTarget(self, **data):
        try:
            DestinationPath = self.storeTargetImage(data["ImagePath"])
            FaceEncoding = self.getFaceEncoding(data["ImagePath"])
            DOB_formatted = datetime.strptime(data["DateOfBirth"], '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')

            data = (
                data["ID"],
                data["FirstName"],
                data["LastName"],
                DestinationPath,
                DOB_formatted,
                data["Notes"],
                data["TodayDate"],
                FaceEncoding
            )

            query = "INSERT INTO criminals VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(query, data)
            self.db.commit()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def removeTargetImage(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def storeTargetImage(self, path):
        try:
            image_filename = os.path.basename(path)
            destination_path = os.path.join("criminals", image_filename)
            shutil.copyfile(path, destination_path)

            return destination_path

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)

    def removeTarget(self, term):
        try:
            query = "DELETE FROM criminals WHERE criminal_id ='" + term + "'"
            self.cursor.execute(query)
            self.db.commit()

            self.removeTargetImage(term)

            self.insertLog("target with ID of {} has been deleted".format(term))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def insertLog(self, event):
        try:
            id = str(uuid.uuid1())[:5]
            today = date.today().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")
            event = event

            data = (id, today, time, event)

            query = "INSERT INTO logs VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, data)
            self.db.commit()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def getTargets(self):
        try:
            self.cursor.execute("SELECT * FROM criminals")
            self.Targets = self.cursor.fetchall()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass
    
    def getlogs(self):
        try:
            self.cursor.execute("SELECT * FROM logs ORDER BY LogDate DESC")
            self.Logs = self.cursor.fetchall()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def searchTarget(self, term):
        try:
            query = "SELECT * FROM criminals WHERE criminal_id = '" + term + "'"
            self.cursor.execute(query)
            self.Targets = self.cursor.fetchall()

            self.insertLog("searching for target with term of {}".format(term))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass

    def searchLogs(self, term):
        try:
            query = "SELECT * FROM logs WHERE LogID LIKE '" + term + "' OR LogEvent LIKE '" + term + "'"
            self.cursor.execute(query)
            self.Targets = self.cursor.fetchall()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(exc_obj)
            pass