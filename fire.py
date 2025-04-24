# main.py
import cv2
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import pyttsx3
import smtplib
from email.message import EmailMessage
import datetime
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Set your Gmail address & App password here
EMAIL_SENDER = "mayurichimane2428@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use App Password from Gmail security settings
EMAIL_RECEIVER = "receiver_email@example.com"  # Where the alert should be sent

class FireDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Fire Detection")
        self.root.geometry("900x600")

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.image_label = ctk.CTkLabel(self.frame, text="")
        self.image_label.pack()

        self.status_label = ctk.CTkLabel(self.frame, text="Status: Waiting for image", font=("Arial", 18))
        self.status_label.pack(pady=10)

        button_frame = ctk.CTkFrame(self.frame)
        button_frame.pack(pady=10)

        self.upload_btn = ctk.CTkButton(button_frame, text="Upload Image", command=self.upload_image)
        self.upload_btn.grid(row=0, column=0, padx=10)

        self.webcam_btn = ctk.CTkButton(button_frame, text="Open Webcam", command=self.open_webcam)
        self.webcam_btn.grid(row=0, column=1, padx=10)

        self.detect_btn = ctk.CTkButton(button_frame, text="Detect Fire", command=self.detect_fire)
        self.detect_btn.grid(row=0, column=2, padx=10)

        self.current_image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.current_image = cv2.imread(file_path)
            self.show_image(self.current_image)
            self.status_label.configure(text="Image uploaded. Ready to detect.")

    def open_webcam(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            self.current_image = frame
            self.show_image(frame)
            self.status_label.configure(text="Webcam image captured. Ready to detect.")
        cap.release()

    def show_image(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.resize((600, 400))
        imgtk = ImageTk.PhotoImage(image=image)
        self.image_label.configure(image=imgtk)
        self.image_label.image = imgtk

    def detect_fire(self):
        if self.current_image is None:
            self.status_label.configure(text="No image to detect.")
            return

        result_img, fire_detected = self.fire_detection_logic(self.current_image.copy())
        self.show_image(result_img)

        if fire_detected:
            self.status_label.configure(text="🔥 Fire Detected!", text_color="red")
            self.save_result(result_img)
            self.log_detection()
            self.text_to_speech_alert("Fire detected! Please take action immediately.")
            self.send_email_alert()
        else:
            self.status_label.configure(text="✅ No Fire Detected.", text_color="green")

    def fire_detection_logic(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([18, 50, 50])
        upper = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        fire_detected = False
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                fire_detected = True
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return frame, fire_detected

    def save_result(self, img):
        if not os.path.exists("results"):
            os.makedirs("results")
        filename = datetime.datetime.now().strftime("results/fire_result_%Y%m%d_%H%M%S.jpg")
        cv2.imwrite(filename, img)
        print(f"Saved: {filename}")

    def log_detection(self):
        with open("fire_log.txt", "a") as log:
            log.write(f"Fire detected at {datetime.datetime.now()}\n")

    def text_to_speech_alert(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def send_email_alert(self):
        msg = EmailMessage()
        msg.set_content("🔥 ALERT: Fire has been detected by the system.\nTime: " + str(datetime.datetime.now()))
        msg["Subject"] = "🔥 Forest Fire Alert"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            print("Email alert sent.")
        except Exception as e:
            print(f"Failed to send email: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = FireDetectionApp(root)
    root.mainloop()
