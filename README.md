# Face Recognition-Based Attendance System

This project implements an automated attendance system using face recognition. It detects and recognizes employees from live video feed and marks their attendance in a MySQL database.

## Features
- Face recognition using OpenCV and face_recognition library
- Live video capture for real-time attendance marking
- MySQL database integration for storing attendance records
- Accuracy display for recognized faces

## Tools & Technologies
- Python, OpenCV, face_recognition
- MySQL for database storage
- NumPy for image processing

## How It Works
1. Load employee images and encode faces.
2. Capture live video and detect faces.
3. Compare detected faces with stored encodings.
4. If a match is found, mark attendance in the database.
5. Display recognition results with accuracy percentage.

## Usage
- Run the script to start the attendance system.
- Press `Esc` to exit the video feed.

## Setup
1. Install required dependencies:
   ```bash
   pip install opencv-python numpy face-recognition mysql-connector-python
   ```
2. Configure MySQL database with employee details.
3. Run the script to start face recognition-based attendance tracking.

## License
This project is for educational purposes only.

