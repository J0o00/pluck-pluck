#
# Useless Exercise Form Detector
#
# This desktop app uses the webcam to detect a person's body
# and provides a rule-based check to see if their squat form is "correct."
# If the form is incorrect, it plays a random, teasing movie dialogue.
#
# This script uses:
# - OpenCV for webcam access
# - Mediapipe for real-time pose estimation
# - Pydub for audio playback
# - CustomTkinter for the graphical user interface (GUI)
#
# NOTE: To run this, you must have the required libraries installed:
#       pip install opencv-python mediapipe pydub customtkinter Pillow
#       Also, pydub requires ffmpeg to be installed on your system.
#
# SETUP: Before running, create a folder named 'audio' in the same
#        directory as this script. Inside 'audio', create two subfolders:
#        'incorrect_form' and 'standing_still'. Place your .mp3 movie dialogue
#        clips in the respective folders.
#
# CHANGES: This version has been updated to use the 'duck.gif' file for the
#          front page animation. The code has been cleaned up for consistency.
#

import cv2
import mediapipe as mp
from pydub import AudioSegment
from pydub.playback import play
import random
import threading
import os
import time
import customtkinter as ctk
import math
import sys
import numpy as np
from pydub import utils
import subprocess
from PIL import Image, ImageTk
from tkinter import font

# --- Configuration ---
# Define the paths to the audio folders
INCORRECT_FORM_AUDIO_PATH = "audio/incorrect_form"
STANDING_STILL_AUDIO_PATH = "audio/standing_still"
# Path to the GIF file provided by the user
GIF_PATH = "duck.gif"

# Set a cooldown period (in seconds) so the app doesn't spam audio
COOLDOWN_PERIOD = 15

# --- Global State ---
last_audio_played_time = 0
audio_is_playing = False
app_running = False
root = None
cap = None
frame_label = None
squat_start_button = None
hand_raise_start_button = None
stop_button = None
status_label = None
back_button = None
# A global variable to hold the PhotoImage to prevent garbage collection
img_tk = None
# Global variable for GIF animation
gif_frames = []
gif_frame_index = 0
gif_label = None
gif_animation_id = None
webcam_update_id = None


squat_counter = 0
squat_state = "UP"  # Can be "UP" or "DOWN"
squat_accuracy = 0.0

hand_raise_counter = 0
hand_raise_state = "DOWN"
hand_raise_accuracy = 0.0

active_exercise = None # 'squat' or 'hand_raise'
prev_landmarks = None
standing_still_counter = 0
max_still_frames = 50

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- Helper Functions ---
def calculate_angle(a, b, c):
    """
    Calculates the angle between three points (a, b, c) in degrees.
    The arguments a, b, and c are Mediapipe landmark objects.
    """
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def play_random_audio(folder_path):
    """
    Selects a random audio file from the specified folder and plays it.
    This function runs on a separate thread to prevent blocking the main video loop.
    """
    global audio_is_playing

    if audio_is_playing:
        return

    try:
        if not os.path.isdir(folder_path):
            print(f"Audio folder not found: {folder_path}")
            return

        audio_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
        if not audio_files:
            print(f"No audio files found in {folder_path}.")
            return

        random_file = random.choice(audio_files)
        audio_path = os.path.join(folder_path, random_file)

        print(f"Playing: {audio_path}")
        audio_is_playing = True

        # Determine the path to ffplay.exe
        ffplay_path = utils.get_prober_name()

        # Run ffplay as a subprocess
        p = subprocess.Popen([ffplay_path, '-nodisp', '-autoexit', audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()

        audio_is_playing = False

    except Exception as e:
        print(f"Error playing audio: {e}")
        audio_is_playing = False

def run_audio_in_thread(folder_path):
    """
    Starts the audio playback function in a new thread.
    """
    audio_thread = threading.Thread(target=play_random_audio, args=(folder_path,))
    audio_thread.daemon = True
    audio_thread.start()

def animate_gif():
    """Animates the GIF on the front page."""
    global root, gif_frames, gif_frame_index, gif_label, gif_animation_id

    try:
        gif_frame_index = (gif_frame_index + 1) % len(gif_frames)
        gif_label.configure(image=gif_frames[gif_frame_index])
        gif_animation_id = root.after(100, animate_gif)
    except Exception as e:
        print(f"Error animating GIF: {e}")

def stop_gif_animation():
    """Stops the GIF animation loop."""
    global root, gif_animation_id
    if gif_animation_id:
        root.after_cancel(gif_animation_id)

# --- Main Application Logic ---
def check_squat_form(landmarks):
    """
    Performs a rule-based check for squat form using Mediapipe landmarks.
    This is a simplified check for a "useless" project, not medical advice.
    """
    global squat_counter, squat_state, squat_accuracy

    # Get landmark points for the hips, knees, and ankles
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

    # Calculate hip angle
    hip_angle = calculate_angle(left_hip, left_knee, left_ankle)

    # Check for correct squat depth and form
    # Standing position: hip angle > 160 degrees
    # Deep squat position: hip angle < 90 degrees
    if hip_angle > 160:
        if squat_state == "DOWN":
            squat_counter += 1
            squat_state = "UP"

        squat_accuracy = 0.0
        return "Standing Up"
    elif hip_angle < 90:
        squat_state = "DOWN"

        squat_accuracy = 100.0
        return "Deep Squat"
    else:
        # Calculate accuracy for an in-between position
        squat_accuracy = (160 - hip_angle) / (160 - 90) * 100

        # Teasing rule: if hip angle is too high, it's a "Shallow squat!"
        if hip_angle > 130:
            return "Shallow squat!"
        else:
            return "Squatting..."

    return "Detecting..."

def check_hand_raise_form(landmarks):
    """
    Checks for a hand raise motion.
    """
    global hand_raise_counter, hand_raise_state, hand_raise_accuracy

    # Get landmark points for arm and head
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]

    # Calculate the angle of the elbow joint
    arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

    if left_wrist.y < left_shoulder.y and arm_angle > 160:
        if hand_raise_state == "DOWN":
            hand_raise_counter += 1
            hand_raise_state = "UP"

        hand_raise_accuracy = 100.0
        return "Hand is raised"
    else:
        hand_raise_state = "DOWN"
        hand_raise_accuracy = 0.0
        return "Hand is down"

def check_standing_still(landmarks):
    """
    Checks for standing still.
    """
    global standing_still_counter, prev_landmarks

    if prev_landmarks is None:
        prev_landmarks = landmarks
        return False

    shoulder_dist = abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x - prev_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x) + \
                    abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y - prev_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y)

    hip_dist = abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x - prev_landmarks[mp_pose.PoseLandmark.LEFT_HIP].x) + \
               abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y - prev_landmarks[mp_pose.PoseLandmark.LEFT_HIP].y)

    if shoulder_dist < 0.01 and hip_dist < 0.01:
        standing_still_counter += 1
        if standing_still_counter > max_still_frames:
            return True
        else:
            return False
    else:
        standing_still_counter = 0

    prev_landmarks = landmarks
    return False

def update_webcam_feed():
    """
    Captures a frame from the webcam, processes it for pose estimation,
    and updates the Tkinter label.
    """
    global app_running, root, cap, frame_label, last_audio_played_time, active_exercise, status_label, img_tk, webcam_update_id

    if not app_running:
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame from webcam.")
        webcam_update_id = root.after(1000, update_webcam_feed)
        return

    # Flip the frame for a mirror effect
    frame = cv2.flip(frame, 1)

    # Process the frame for pose estimation
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    display_text = "Click a button to start an exercise"
    text_color = "black"

    # --- NEW: Prioritized feedback logic ---
    play_standing_still_audio = False

    if results.pose_landmarks:
        tease_message = ""

        # Priority 1: Check for incorrect form
        if active_exercise == 'squat':
            tease_message = check_squat_form(results.pose_landmarks.landmark)
            if "Shallow squat!" in tease_message:
                text_color = "red"
                if time.time() - last_audio_played_time > COOLDOWN_PERIOD:
                    run_audio_in_thread(INCORRECT_FORM_AUDIO_PATH)
                    last_audio_played_time = time.time()

                display_text = "enthan mone, kurchu kanji edukate"
            else:
                text_color = "black"
                display_text = f"Squats: {squat_counter} | Accuracy: {squat_accuracy:.0f}%"

        elif active_exercise == 'hand_raise':
            tease_message = check_hand_raise_form(results.pose_landmarks.landmark)
            if "Hand is down" in tease_message:
                text_color = "red"
                if time.time() - last_audio_played_time > COOLDOWN_PERIOD:
                    run_audio_in_thread(INCORRECT_FORM_AUDIO_PATH)
                    last_audio_played_time = time.time()

                display_text = "enthan mone, kurchu kanji edukate"
            else:
                text_color = "black"
                display_text = f"Hand Raises: {hand_raise_counter} | Accuracy: {hand_raise_accuracy:.0f}%"

        # Priority 2: Check for standing still (only if no incorrect form)
        if (("Shallow" not in tease_message) and ("down" not in tease_message)):
            if check_standing_still(results.pose_landmarks.landmark):
                play_standing_still_audio = True
                text_color = "red"
                display_text = "Onnu angangi cheyada"

        if play_standing_still_audio and (time.time() - last_audio_played_time > COOLDOWN_PERIOD):
            run_audio_in_thread(STANDING_STILL_AUDIO_PATH)
            last_audio_played_time = time.time()

        # Draw the pose landmarks on the frame
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
        )

    else: # No human detected
        text_color = "black"
        display_text = "Detecting human..."

    status_label.configure(text=display_text, text_color=text_color)
    # --- END NEW ---


    # Convert the OpenCV frame to an image for CustomTkinter
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img_tk = ImageTk.PhotoImage(image=img)
    frame_label.configure(image=img_tk)
    frame_label.image = img_tk

    # Loop the function
    webcam_update_id = root.after(10, update_webcam_feed)

def start_squat_logic():
    """Starts the squat detection loop."""
    global active_exercise, squat_counter, hand_raise_counter, prev_landmarks
    active_exercise = 'squat'
    squat_counter = 0
    hand_raise_counter = 0
    prev_landmarks = None
    start_app_logic()

def start_hand_raise_logic():
    """Starts the hand raise detection loop."""
    global active_exercise, squat_counter, hand_raise_counter, prev_landmarks
    active_exercise = 'hand_raise'
    squat_counter = 0
    hand_raise_counter = 0
    prev_landmarks = None
    start_app_logic()

def stop_webcam_feed():
    """Stops the webcam and cancels the update loop."""
    global app_running, cap, root, webcam_update_id
    if webcam_update_id:
        root.after_cancel(webcam_update_id)
        webcam_update_id = None
    if cap and cap.isOpened():
        cap.release()

def start_app_logic():
    """Starts the webcam and processing loop."""
    global app_running, cap, squat_start_button, hand_raise_start_button, stop_button, back_button
    if app_running:
        return

    app_running = True
    print(f"App started. Current exercise: {active_exercise}")

    # Disable the start buttons and enable the stop button
    squat_start_button.configure(state="disabled")
    hand_raise_start_button.configure(state="disabled")
    stop_button.configure(state="normal")
    back_button.configure(state="normal")


    # Initialize the webcam
    # Loop through a few camera indices to find a working webcam
    camera_index = 0
    cap = cv2.VideoCapture(camera_index)
    while not cap.isOpened() and camera_index < 5:
        camera_index += 1
        print(f"Could not open camera {camera_index-1}. Trying camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Could not open any webcam. Please ensure a camera is connected and not in use by another application.")
        app_running = False
        squat_start_button.configure(state="normal")
        hand_raise_start_button.configure(state="normal")
        return

    # Start the update loop
    update_webcam_feed()

def stop_app_logic():
    """Stops the webcam and processing loop."""
    global app_running, cap, squat_start_button, hand_raise_start_button, stop_button, back_button, prev_landmarks
    if not app_running:
        return

    app_running = False
    prev_landmarks = None
    print("App stopped.")

    # Enable the start buttons and disable the stop button
    squat_start_button.configure(state="normal")
    hand_raise_start_button.configure(state="normal")
    stop_button.configure(state="disabled")
    back_button.configure(state="normal")

    if cap and cap.isOpened():
        cap.release()

def create_front_page():
    """Creates the front page of the application."""
    global root, status_label, gif_frames, gif_label

    # Set the appearance mode and color theme
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.title("pluck pluck")
    root.geometry("600x600")
    root.configure(fg_color="#FFFF00") # Lighter yellow theme

    main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color="#FFFF00")
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(main_frame, text="pluck pluck",
                               font=ctk.CTkFont(family="Courier", size=40, weight="bold"), text_color="black")
    title_label.pack(pady=(20, 10))


    start_button = ctk.CTkButton(main_frame, text="Start App", command=lambda: [root.destroy(), create_gui()],
                                 fg_color="#9370DB", hover_color="#A585E2", text_color="white",
                                 font=ctk.CTkFont(size=16, weight="bold"), corner_radius=10)
    start_button.pack(pady=10)

    # --- NEW: Add GIF animation to the front page ---
    gif_label = ctk.CTkLabel(main_frame, text="")
    gif_label.pack(side="bottom", anchor="sw", padx=10, pady=10)

    # Check if the GIF file exists using the standardized GIF_PATH
    if os.path.exists(GIF_PATH):
        try:
            # Load the GIF frames
            gif = Image.open(GIF_PATH)
            gif_frames = []
            for frame in range(gif.n_frames):
                gif.seek(frame)
                resized_frame = gif.resize((750, 750), Image.Resampling.LANCZOS)
                gif_frames.append(ImageTk.PhotoImage(resized_frame))

            # Start the animation
            animate_gif()
        except Exception as e:
            print(f"Error loading GIF: {e}")
    else:
        print(f"Warning: GIF file '{GIF_PATH}' not found.")

    root.mainloop()

def create_gui():
    """Creates the main CustomTkinter GUI window and its widgets."""
    global root, frame_label, squat_start_button, hand_raise_start_button, stop_button, status_label, back_button

    root = ctk.CTk()
    root.title("Useless Exercise Form Detector")
    root.geometry("600x600")
    root.configure(fg_color="#FFFF00") # Lighter yellow theme

    main_frame = ctk.CTkFrame(root, corner_radius=20, fg_color="#FFFF00")
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    task_label = ctk.CTkLabel(main_frame, text="Choose the task:", font=ctk.CTkFont(size=16, weight="bold"), text_color="black")
    task_label.pack(pady=(10, 5))

    frame_label = ctk.CTkLabel(main_frame, text="", bg_color="black")
    frame_label.pack(pady=10)

    button_frame = ctk.CTkFrame(main_frame, fg_color="#FFFF00")
    button_frame.pack(pady=10)

    squat_start_button = ctk.CTkButton(button_frame, text="Start Squats", command=start_squat_logic,
                                       fg_color="#9370DB", hover_color="#A585E2", text_color="white",
                                       font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10,
                                       width=200, height=50)
    squat_start_button.pack(pady=5, expand=True, fill="both")

    hand_raise_start_button = ctk.CTkButton(button_frame, text="Start Hand Raise", command=start_hand_raise_logic,
                                           fg_color="#9370DB", hover_color="#A585E2", text_color="white",
                                           font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10,
                                           width=200, height=50)
    hand_raise_start_button.pack(pady=5, expand=True, fill="both")

    stop_button = ctk.CTkButton(button_frame, text="Stop", command=stop_app_logic, state="disabled",
                                fg_color="#D32F2F", hover_color="#E53935", text_color="white",
                                font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10,
                                width=200, height=50)
    stop_button.pack(pady=5, expand=True, fill="both")

    back_button = ctk.CTkButton(button_frame, text="Back", command=lambda: [stop_app_logic(), root.destroy(), create_front_page()],
                                fg_color="gray", hover_color="darkgray", text_color="white",
                                font=ctk.CTkFont(size=14, weight="bold"), corner_radius=10,
                                width=200, height=50)
    back_button.pack(pady=5, expand=True, fill="both")

    status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color="black")
    status_label.pack(pady=10)

    def on_closing():
        global app_running, cap
        app_running = False
        if cap and cap.isOpened():
            cap.release()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter main loop
    root.mainloop()

def run_app():
    """
    A simple function to run the app from a terminal.
    """
    create_front_page()

if __name__ == "__main__":

    # --- Set a local temporary directory for pydub ---
    try:
        temp_dir = os.path.join(os.getcwd(), 'temp_pydub')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        utils.get_pydub_temp_dir = lambda: temp_dir
    except Exception as e:
        print(f"Warning: Could not set local temp directory for pydub. {e}")
        # We will proceed, but there may be issues with audio playback.

    run_app()

