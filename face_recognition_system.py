import cv2
import numpy as np
import face_recognition
import mysql.connector
from datetime import datetime
import os

# Connect to the MySQL database
conn = mysql.connector.connect(host='localhost', user="root", password="Password@123", database="safetywhat")
mycursor = conn.cursor()


mycursor.execute("SELECT picture, name FROM employee_details")
data = mycursor.fetchall()
# print(data)

images = []
student_names = []


for image_path, name in data:
    cur_img = cv2.imread(image_path)
    # cur_img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    images.append(cur_img)
    student_names.append(name)

# print(student_names)
# print(images)

# Function to find face encodings for a list of images
def find_encodings(images):
    encode_list = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)  # Find face locations
        
        if len(face_locations) > 0:
            encode = face_recognition.face_encodings(img, face_locations)[0]
            encode_list.append(encode)
        else:
            print("No face found in the image.")
    
    return encode_list  # Return the list of face encodings

# Use student_images for face recognition
known_face_encodings = find_encodings(images)
known_face_names = student_names

# Initialize some variables for live video capture
video_capture = cv2.VideoCapture(0)
frame_count = 0
start_time = datetime.now()
fpslist = []

# Dictionary to keep track of last attendance date for each recognized face
last_attendance_date = {}

# Function to mark attendance for a recognized face
def markattendance(name):
    now = datetime.now()
    date = now.strftime('%d-%B-%Y')
    time = now.strftime('%I:%M:%S %p')

    # Check if the face has already been recognized today
    if name not in last_attendance_date or last_attendance_date[name] != date:
        mycursor.execute("SELECT * FROM employee_present WHERE name=%s AND dat=%s", (name, date))
        existing_records = mycursor.fetchall()

        if not existing_records:
            sql = "INSERT INTO employee_present (name, time, dat) VALUES (%s, %s, %s)"
            values = (name, time, date)
            mycursor.execute(sql, values)
            conn.commit()

            last_attendance_date[name] = date
            status_text = f"Attendance marked for {name} on {date}"

            # Updating status in the Total_students table
            update_status_query = "UPDATE employee_details SET status = %s WHERE name = %s"
            mycursor.execute(update_status_query, ('Present', name))
            conn.commit()
        else:
            status_text = f"Attendance already marked for {name} on {date}"

    else:
        status_text = f"Attendance marked for {name} on {date}"

    return status_text



while True:
    success, frame = video_capture.read()

    frame = cv2.resize(frame,(1200,720))

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding,tolerance=0.6)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            accuracy_percentage = (1 - face_distances[best_match_index]) * 100

        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        status_text = markattendance(name).upper()
        cv2.putText(frame, text=status_text, org=(left-150, top + 205), fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=0.5, color=(0,0,255), thickness=2)
        cv2.putText(frame, f"Accuracy: {accuracy_percentage:.2f}%", (left + 6, top - 30), font, 0.5, (0, 0, 255), 1)

        if name != "Unknown":
            markattendance(name)

    frame_count += 1
    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()

    if elapsed_time >= 1:
        fps = frame_count / elapsed_time
        fpslist.append(fps)

        frame_count = 0
        start_time = datetime.now()

    cv2.imshow('ATTENDANCE SYSTEM ', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

# Close the database connection
conn.close()

# Calculate average FPS(frame per second)
avg_fps = sum(fpslist) / len(fpslist)
print(f"Average FPS: {avg_fps:.2f}")
