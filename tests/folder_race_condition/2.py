import sys
import os
import csv
import time
import random
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt, Signal
from pynput import keyboard

class FakeDataGenerator:
    def __init__(self):
        self.acc_data = lambda: (random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2))
        self.ibi_data = lambda: random.uniform(0, 100)
        self.ecg_data = lambda: random.uniform(0, 20)

class MainWindow(QWidget):
    start_recording_signal = Signal()
    stop_recording_signal = Signal()
    def __init__(self):
        super().__init__()
        self.start_recording_signal.connect(self.start_recording)
        self.stop_recording_signal.connect(self.stop_recording)
        self.setWindowTitle('Fake Polar Data Generator')
        self.layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Press '#' to start/stop recording")
        self.layout.addWidget(self.status_label)

        self.recording = False
        self.data_generator = FakeDataGenerator()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.generate_and_write_data)

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('#'):
            self.toggle_recording()

    def toggle_recording(self):
        if not self.recording:
            self.start_recording_signal.emit()
        else:
            self.stop_recording_signal.emit()

    def start_recording(self):
        self.recording_folder = self.create_recording_folder()
        print(f"Recording started. Data will be saved in {self.recording_folder}")
        self.open_csv_files()
        self.recording = True
        self.timer.start(200)  # Generate data every 0.2 seconds
        self.status_label.setText("Recording... Press '#' to stop")

    def stop_recording(self):
        self.timer.stop()
        self.close_csv_files()
        self.recording = False
        self.status_label.setText("Recording stopped. Press '#' to start")

    def create_recording_folder(self):
        base_folder = os.path.dirname(sys.executable)
        date_str = datetime.now().strftime("%d_%m_%Y")

        # Find the highest session number
        session_number = 1
        while True:
            session_folder = f"{date_str}_session{session_number}"
            full_path = os.path.join(base_folder, session_folder)
            Polar_path = os.path.join(full_path, "Polar")
            
            if not os.path.exists(Polar_path):
                break
            session_number += 1

        # Create the new session folder and Polar subfolder
        os.makedirs(Polar_path)
        print(Polar_path)
        return Polar_path

    def open_csv_files(self):
        self.files = {##
            'acc': open(os.path.join(self.recording_folder, 'Polar_acc_data.csv'), 'w', newline=''),
            'ibi': open(os.path.join(self.recording_folder, 'Polar_ibi_data.csv'), 'w', newline=''),
            'ecg': open(os.path.join(self.recording_folder, 'Polar_ecg_data.csv'), 'w', newline=''),
        }
        self.writers = {k: csv.writer(v) for k, v in self.files.items()}

    def close_csv_files(self):
        for file in self.files.values():
            file.close()

    def generate_and_write_data(self):
        timestamp = int(time.time() * 1e9)  # nanoseconds
        
        acc_data = self.data_generator.acc_data()
        self.writers['acc'].writerow([timestamp, *acc_data])
        
        for data_type in ['ibi', 'ecg', 'acc',]:
            value = getattr(self.data_generator, f"{data_type}_data")()
            self.writers[data_type].writerow([timestamp, value])
        
        for file in self.files.values():
            file.flush()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
