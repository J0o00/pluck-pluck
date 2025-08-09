<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />

# **Pluck Pluck** 🎯

## Basic Details  
### Team Name: **Sentinels**  

### Team Members  
- **Team Lead:** Chrysler K.M – Christ College of Engineering, Irinjalakuda  
- **Member 2:** Jovial Joyson – Christ College of Engineering, Irinjalakuda  

---

### Project Description  
The project, whimsically named **"Pluck Pluck"**, is a desktop application designed to provide humorous, real-time feedback on a person's exercise form. It uses computer vision to track movements and plays funny movie dialogues when the form is incorrect or when the person is inactive.  

---

### The Problem (that doesn’t exist)  
In a world of over-optimized fitness trackers, we saw a glaring gap: a lack of unnecessary, judgmental digital coaches. We've solved the problem of having to rely on self-motivation by creating an app that actively teases you for bad form.  

---

### The Solution (that nobody asked for)  
**"Pluck Pluck"** is a desktop app that uses machine learning to detect squats and hand raises. Instead of offering helpful advice, it critiques your form in a playful and passive-aggressive manner with movie dialogues. It's the fitness coach you didn’t know you needed, and probably don’t.  

---

## Technical Details  

### Technologies/Components Used  

**For Software:**  
- **Languages used:** Python  
- **Frameworks used:** CustomTkinter (GUI), Mediapipe (Pose Estimation)  
- **Libraries used:** OpenCV, Pydub, NumPy, Pillow  
- **Tools used:** FFmpeg (for audio playback)  

**For Hardware:**  
- **Main components:** Laptop with integrated or external webcam  
- **Specifications:** Modern laptop, good processor, minimum 8GB RAM for smooth real-time processing  
- **Tools required:** Git for version control  

---

### Implementation  

**Installation** 
opencv-python: Used for accessing the webcam and processing video frames.

mediapipe: The core machine learning library for real-time pose estimation.

pydub: A high-level Python library for working with audio files, used to play your movie dialogues.

customtkinter: A library that extends Tkinter to create modern, attractive user interfaces.

Pillow: A library for handling image files, used for displaying the webcam feed and the animated GIF.

External Tool
FFmpeg: This is a crucial command-line tool that pydub uses for playing audio files. You must download the executable files from the official FFmpeg website and add the bin folder to your system's PATH.

Clone the repository:  
```bash
git clone https://github.com/J0o00/USELESSPROJECT.git
```

Create and activate a virtual environment:  
```bash
python3.12 -m venv useless-project-env
.\useless-project-env\Scripts\activate
```

Install the required libraries:  
```bash
pip install opencv-python mediapipe pydub customtkinter Pillow
```

Download and set up **FFmpeg** (required for audio in Pydub):  
- Download from [FFmpeg Builds](https://ffmpeg.org/download.html)  
- Add `bin` folder to system PATH  

Download and place the audio & GIF files:  
- **Audio files:** [Google Drive Link](https://drive.google.com/drive/folders/1CRWFIQakxHDFg6jeqSOUMj7ZJQZpFr70?usp=drive_link)  
- **GIF file:** [Google Drive Link](https://drive.google.com/file/d/1bnv5SWeGrKLKLX86VkiJe7Hgj9BaS0cZ/view?usp=drive_link)  

Folder structure:  
```
project/
│── audio/
│   ├── incorrect_form/
│   └── standing_still/
│── duck.gif
│── Useless Exercise Form Detector.py
```

**Run the app:**  
```bash
python "Useless Exercise Form Detector.py"
```

---

## Project Documentation  

### Screenshots  
![Screenshot1][(Add screenshot 1 here)](https://drive.google.com/file/d/1uG6jriNbz7ZWAf1rSFW9NtPB9c67AGTs/view?usp=drive_link)  
*Detecting incorrect squat form and triggering a funny dialogue*  

![Screenshot2][(Add screenshot 2 here) ](https://drive.google.com/file/d/1jZWk9LzlgmPe655ymwsSRQl8ofAAZfTE/view?usp=drive_link) 
*Passive-aggressive popup while user is idle*  

![Screenshot3][(Add screenshot 3 here)](https://drive.google.com/file/d/11qg8AXTqtuzhOJ-_p4vjB-WOV6GDJ4s-/view?usp=drive_link)  
*GUI showing live pose estimation*  

---

### Diagrams  
![Workflow](Add diagram here)  
*Webcam → Pose Estimation (MediaPipe) → Form Analysis → Funny Dialogue Audio Output*  

---

## Team Contributions  
- **Chrysler K.M:** Project ideation, GUI design, integration of Mediapipe with Tkinter, testing  
- **Jovial Joyson:** Audio integration with Pydub, FFmpeg setup, bug fixes, repository management  
- **An:** GIF integration, funny dialogue scripting, resource collection  

---

Made with ❤️ at **TinkerHub Useless Projects**  

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)  
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)  
