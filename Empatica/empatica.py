import sys
import socket
import csv
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QThread, Signal, Qt
import pyqtgraph as pg
from pynput import keyboard
from collections import deque
import os
from datetime import datetime
import sys

# E4 Streaming Server configuration
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 28000

class DataReceiver(QThread):
    data_received = Signal(str)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_ADDRESS, SERVER_PORT))

        # Send commands to connect and subscribe to data streams
        sock.sendall(b'device_list\r\n')
        response = sock.recv(1024).decode('utf-8')
        device_id = response.split('|')[1].strip().split(' ')[0]

        sock.sendall(f'device_connect {device_id}\r\n'.encode())
        sock.recv(1024)

        streams = [
            "acc",
            "bat",
            "bvp",
            "gsr",
            "ibi",
            "tag",
            "tmp"
            ]
        # source: https://developer.empatica.com/windows-streaming-server-commands.html
        # STREAM SUBSCRIPTIONS
        # The available stream subscriptions are:

        # acc - 3-axis acceleration
        # bvp - Blood Volume Pulse
        # gsr - Galvanic Skin Response
        # ibi - Interbeat Interval and Heartbeat
        # tmp - Skin Temperature
        # bat - Device Battery
        # tag - Tag taken from the device (by pressing the button)

        for stream in streams:
            print(stream)
            time.sleep(0.7)
            sock.sendall(f'device_subscribe {stream} ON\r\n'.encode())
            sock.recv(1024)

        while True:
            data = sock.recv(1024).decode('utf-8').strip()
            if data:
                self.data_received.emit(data)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Empatica E4 Data Plotter')

        layout = QVBoxLayout()

        self.acc_plot = pg.PlotWidget(title='Acceleration')
        self.bvp_plot = pg.PlotWidget(title='Blood Volume Pulse')
        self.gsr_plot = pg.PlotWidget(title='Galvanic Skin Response')
        self.tmp_plot = pg.PlotWidget(title='Skin Temperature')
        self.ibi_plot = pg.PlotWidget(title='Interbeat Interval')
        self.hr_plot = pg.PlotWidget(title='Heart Rate')

        self.acc_timestamp_label = QLabel()
        self.bvp_timestamp_label = QLabel()
        self.gsr_timestamp_label = QLabel()
        self.tmp_timestamp_label = QLabel()
        self.ibi_timestamp_label = QLabel()
        self.hr_timestamp_label = QLabel()

        layout.addWidget(self.acc_plot)
        layout.addWidget(self.acc_timestamp_label)
        layout.addWidget(self.bvp_plot)
        layout.addWidget(self.bvp_timestamp_label)
        layout.addWidget(self.gsr_plot)
        layout.addWidget(self.gsr_timestamp_label)
        layout.addWidget(self.tmp_plot)
        layout.addWidget(self.tmp_timestamp_label)
        layout.addWidget(self.ibi_plot)
        layout.addWidget(self.ibi_timestamp_label)
        layout.addWidget(self.hr_plot)
        layout.addWidget(self.hr_timestamp_label)

        self.log_button = QPushButton('Start Logging')
        self.log_button.clicked.connect(self.toggle_logging)
        layout.addWidget(self.log_button)

        self.setLayout(layout)

        self.buffer_size = 100
        self.acc_data = deque(maxlen=self.buffer_size)
        self.bvp_data = deque(maxlen=self.buffer_size)
        self.gsr_data = deque(maxlen=self.buffer_size)
        self.tmp_data = deque(maxlen=self.buffer_size)
        self.ibi_data = deque(maxlen=self.buffer_size)
        self.hr_data = deque(maxlen=self.buffer_size)

        self.acc_curve = self.acc_plot.plot()
        self.bvp_curve = self.bvp_plot.plot()
        self.gsr_curve = self.gsr_plot.plot()
        self.tmp_curve = self.tmp_plot.plot()
        self.ibi_curve = self.ibi_plot.plot()
        self.hr_curve = self.hr_plot.plot()

        self.logging_enabled = False
        self.acc_file = None
        self.bvp_file = None
        self.gsr_file = None
        self.tmp_file = None
        self.ibi_file = None
        self.hr_file = None
        self.acc_writer = None
        self.bvp_writer = None
        self.gsr_writer = None
        self.tmp_writer = None
        self.ibi_writer = None
        self.hr_writer = None

        self.data_receiver = DataReceiver()
        self.data_receiver.data_received.connect(self.update_plot)
        self.data_receiver.start()

        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def create_recording_folder(self):
        base_folder = os.path.dirname(sys.executable)
        date_str = datetime.now().strftime("%d_%m_%Y")

        # Find the highest session number
        session_number = 1
        while True:
            session_folder = f"{date_str}_session{session_number}"
            full_path = os.path.join(base_folder, session_folder)
            empatica_path = os.path.join(full_path, "Empatica")
            
            if not os.path.exists(empatica_path):
                break
            session_number += 1

        # Create the new session folder and Empatica subfolder
        os.makedirs(empatica_path)
        print(empatica_path)
        return empatica_path


    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('#'):
            self.toggle_logging()

    def update_plot(self, data):
        parts = data.split()
        if len(parts) >= 3 and parts[0].startswith('E4_'):
            stream_type, timestamp, *values = parts
            timestamp = float(timestamp)
            milliseconds = int(timestamp * 1e3)
            formatted_time = time.strftime("%H:%M:%S", time.localtime(timestamp)) + f".{milliseconds % 1000:03d}"

            if self.logging_enabled:
                self.write_to_file(stream_type, milliseconds, values)

            if stream_type == 'E4_Acc':
                if len(values) == 3:
                    x, y, z = map(float, values)
                    self.acc_data.append((timestamp, x, y, z))
                    self.acc_curve.setData([d[0] for d in self.acc_data], [d[1] for d in self.acc_data])
                    self.acc_timestamp_label.setText(f"Last Timestamp: {formatted_time}")

            elif stream_type == 'E4_Bvp':
                value = float(values[0])
                self.bvp_data.append((timestamp, value))
                self.bvp_curve.setData([d[0] for d in self.bvp_data], [d[1] for d in self.bvp_data])
                self.bvp_timestamp_label.setText(f"Last Timestamp: {formatted_time}")

            elif stream_type == 'E4_Gsr':
                value = float(values[0])
                self.gsr_data.append((timestamp, value))
                self.gsr_curve.setData([d[0] for d in self.gsr_data], [d[1] for d in self.gsr_data])
                self.gsr_timestamp_label.setText(f"Last Timestamp: {formatted_time}")

            elif stream_type == 'E4_Temperature':
                value = float(values[0])
                self.tmp_data.append((timestamp, value))
                self.tmp_curve.setData([d[0] for d in self.tmp_data], [d[1] for d in self.tmp_data])
                self.tmp_timestamp_label.setText(f"Last Timestamp: {formatted_time}")

            elif stream_type == 'E4_Ibi':
                value = float(values[0])
                self.ibi_data.append((timestamp, value))
                self.ibi_curve.setData([d[0] for d in self.ibi_data], [d[1] for d in self.ibi_data])
                self.ibi_timestamp_label.setText(f"Last Timestamp: {formatted_time}")
                print(f"Received Ibi: {value}")

            elif stream_type == 'E4_Hr':
                value = float(values[0])
                self.hr_data.append((timestamp, value))
                self.hr_curve.setData([d[0] for d in self.hr_data], [d[1] for d in self.hr_data])
                self.hr_timestamp_label.setText(f"Last Timestamp: {formatted_time}")
                print(f"Received HR: {value}")
        else:
            print(f"Received non-data message: {data}")
            if self.logging_enabled:
                self.write_non_data_to_file(data)

    def write_to_file(self, stream_type, nanoseconds, values):
        if stream_type == 'E4_Acc':
            if len(values) == 3:
                x, y, z = map(float, values)
                self.acc_writer.writerow([nanoseconds, x, y, z])
                self.acc_file.flush()
        elif stream_type == 'E4_Bvp':
            value = float(values[0])
            self.bvp_writer.writerow([nanoseconds, value])
            self.bvp_file.flush()
        elif stream_type == 'E4_Gsr':
            value = float(values[0])
            self.gsr_writer.writerow([nanoseconds, value])
            self.gsr_file.flush()
        elif stream_type == 'E4_Temperature':
            value = float(values[0])
            self.tmp_writer.writerow([nanoseconds, value])
            self.tmp_file.flush()
        elif stream_type == 'E4_Ibi':
            value = float(values[0])
            self.ibi_writer.writerow([nanoseconds, value])
            self.ibi_file.flush()
        elif stream_type == 'E4_Hr':
            value = float(values[0])
            self.hr_writer.writerow([nanoseconds, value])
            self.hr_file.flush()

    def write_non_data_to_file(self, data):
        self.non_data_writer.writerow([int(time.time() * 1e9), data])
        self.non_data_file.flush()

    def toggle_logging(self):
        if not self.logging_enabled:
            recording_folder = self.create_recording_folder()
            self.acc_file = open(os.path.join(recording_folder, 'empatica_acc_data.csv'), 'w', newline='')
            self.bvp_file = open(os.path.join(recording_folder, 'empatica_bvp_data.csv'), 'w', newline='')
            self.gsr_file = open(os.path.join(recording_folder, 'empatica_gsr_data.csv'), 'w', newline='')
            self.tmp_file = open(os.path.join(recording_folder, 'empatica_temp_data.csv'), 'w', newline='')
            self.ibi_file = open(os.path.join(recording_folder, 'empatica_ibi_data.csv'), 'w', newline='')
            self.hr_file = open(os.path.join(recording_folder, 'empatica_hr_data.csv'), 'w', newline='')
            self.non_data_file = open(os.path.join(recording_folder, 'empatica_non_data_log.csv'), 'w', newline='')

            self.acc_writer = csv.writer(self.acc_file)
            self.bvp_writer = csv.writer(self.bvp_file)
            self.gsr_writer = csv.writer(self.gsr_file)
            self.tmp_writer = csv.writer(self.tmp_file)
            self.ibi_writer = csv.writer(self.ibi_file)
            self.hr_writer = csv.writer(self.hr_file)
            self.non_data_writer = csv.writer(self.non_data_file)
            self.log_button.setText('Stop Logging')
            self.logging_enabled = True
            print("Logging started")
        else:
            self.acc_file.close()
            self.bvp_file.close()
            self.gsr_file.close()
            self.tmp_file.close()
            self.ibi_file.close()
            self.hr_file.close()
            self.non_data_file.close()
            self.log_button.setText('Start Logging')
            self.logging_enabled = False
            print("Logging stopped")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())