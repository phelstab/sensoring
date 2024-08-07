import wave
import os
from PySide6.QtMultimedia import QAudioFormat, QAudioSource, QMediaDevices
from PySide6.QtCore import QIODevice, QTimer, QElapsedTimer
from PySide6.QtWidgets import QLabel

RESOLUTION = 4

class AudioRecorder:
    def __init__(self):
        self.audio_input = None
        self.io_device = None
        self.is_audio_recording = False
        self.audio_data = bytearray()
        self.timer = None
        self.elapsed_timer = QElapsedTimer()
        self.time_label = QLabel("00:00:00")

    def ready_audio(self):
        format_audio = QAudioFormat()
        format_audio.setSampleRate(16000)
        format_audio.setChannelCount(7)
        format_audio.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        # Get the Azure Kinect DK audio input device
        input_device = None
        for device in QMediaDevices.audioInputs():
            if "Azure Kinect" in device.description():
                input_device = device
                break

        if input_device is None:
            raise ValueError("Azure Kinect DK audio device not found.")

        # Create the QAudioSource with the selected input device and format
        self.audio_input = QAudioSource(input_device, format_audio)

    def start_audio(self):
        self.ready_audio()
        self.io_device = self.audio_input.start()
        self.is_audio_recording = True

        # Clear the audio data
        self.audio_data = bytearray()

        # Start a timer to read audio data periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_audio_data)
        self.timer.start(100)  # Adjust the interval as needed

        # Start the elapsed timer
        self.elapsed_timer.start()
        self.update_time_label()

    def stop_audio(self):
        self.audio_input.stop()
        self.io_device = None
        self.is_audio_recording = False

        # Stop the timer
        if self.timer:
            self.timer.stop()
            self.timer = None

        # Use the Windows Videos folder
        videos_folder = os.path.join(os.path.expanduser("~"), "Videos")
        audio_file_path = os.path.join(videos_folder, f"recorded_audio_{self.elapsed_timer.elapsed()}.wav")

        with wave.open(audio_file_path, "wb") as wav_file:
            wav_file.setnchannels(7)
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(16000)
            wav_file.writeframes(self.audio_data)

        print(f"Audio saved to {audio_file_path}")

        # Stop the elapsed timer
        self.elapsed_timer.invalidate()

    def read_audio_data(self):
        if self.is_audio_recording:
            data = self.io_device.readAll()
            available_samples = data.size() // RESOLUTION

            # Append the audio data to the bytearray
            self.audio_data.extend(data.data())

            # Update the time label
            self.update_time_label()

            return data, available_samples
        return None, 0

    def update_time_label(self):
        elapsed_ms = self.elapsed_timer.elapsed()
        hours = elapsed_ms // 3600000
        minutes = (elapsed_ms % 3600000) // 60000
        seconds = (elapsed_ms % 60000) // 1000
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    recorder = AudioRecorder()

    window = QWidget()
    layout = QVBoxLayout()

    start_button = QPushButton("Start Recording")
    stop_button = QPushButton("Stop Recording")

    start_button.clicked.connect(recorder.start_audio)
    stop_button.clicked.connect(recorder.stop_audio)

    layout.addWidget(start_button)
    layout.addWidget(stop_button)
    layout.addWidget(recorder.time_label)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())
