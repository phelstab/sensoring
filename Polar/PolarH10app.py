import asyncio
from bleak import BleakScanner
from PolarH10 import PolarH10
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox
from PySide6.QtCore import QThread, Signal, Slot, QObject, QTimer
import numpy as np
import pyqtgraph as pg
from collections import deque
import csv
import time
from pynput import keyboard
import io
import os
from datetime import datetime
import sys
class DeviceScanner(QThread):
    devices_found = Signal(list)

    async def scan_devices(self):
        devices = await BleakScanner.discover()
        polar_devices = [device for device in devices if device.name and "Polar H10" in device.name]
        self.devices_found.emit(polar_devices)

    def run(self):
        asyncio.run(self.scan_devices())

class PolarSensorWorker(QThread):
    connected = Signal()
    device_info = Signal(str)
    ibi_data = Signal(tuple)
    acc_data = Signal(tuple)
    ecg_data = Signal(tuple)

    def __init__(self, polar_sensor):
        super().__init__()
        self.polar_sensor = polar_sensor
        self.recording_enabled = False
        self.ibi_buffer = io.StringIO()
        self.acc_buffer = io.StringIO()
        self.ecg_buffer = io.StringIO()
        self.csv_writers = {
            'ibi': csv.writer(self.ibi_buffer, lineterminator='\n'),
            'acc': csv.writer(self.acc_buffer, lineterminator='\n'),
            'ecg': csv.writer(self.ecg_buffer, lineterminator='\n')
        }
        self.buffer_size = 1000
        self.buffer_count = 0
        self.running = True
        self.recording_folder = ""

    async def connect_and_start_streams(self):
        try:
            await self.polar_sensor.connect()
            self.connected.emit()

            await self.polar_sensor.get_device_info()
            device_info = await self.polar_sensor.print_device_info()
            self.device_info.emit(device_info)

            await self.polar_sensor.start_hr_stream()
            await self.polar_sensor.start_acc_stream()
            await self.polar_sensor.start_ecg_stream()

            while self.running:
                await self.process_data()
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Error in connect_and_start_streams: {e}")
        finally:
            await self.polar_sensor.disconnect()

    async def process_data(self):
        while not self.polar_sensor.ibi_queue_is_empty():
            timestamp, ibi_data = self.polar_sensor.dequeue_ibi()
            self.ibi_data.emit((timestamp, ibi_data))
            if self.recording_enabled:
                self.write_to_buffer('ibi', [timestamp, ibi_data])

        while not self.polar_sensor.acc_queue_is_empty():
            timestamp, acc_data = self.polar_sensor.dequeue_acc()
            self.acc_data.emit((timestamp, acc_data))
            if self.recording_enabled:
                self.write_to_buffer('acc', [timestamp] + list(acc_data))

        while not self.polar_sensor.ecg_queue_is_empty():
            timestamp, ecg_data = self.polar_sensor.dequeue_ecg()
            self.ecg_data.emit((timestamp, ecg_data))
            if self.recording_enabled:
                self.write_to_buffer('ecg', [timestamp, ecg_data])

        if self.buffer_count >= self.buffer_size:
            self.flush_buffers()

    def run(self):
        asyncio.run(self.connect_and_start_streams())

    def stop(self):
        self.running = False

    def write_to_buffer(self, data_type, data):
        self.csv_writers[data_type].writerow(data)
        self.buffer_count += 1

    def flush_buffers(self):
        with open(os.path.join(self.recording_folder, 'polar_ibi_data.csv'), 'a') as f:
            f.write(self.ibi_buffer.getvalue())
        with open(os.path.join(self.recording_folder, 'polar_acc_data.csv'), 'a') as f:
            f.write(self.acc_buffer.getvalue())
        with open(os.path.join(self.recording_folder, 'polar_ecg_data.csv'), 'a') as f:
            f.write(self.ecg_buffer.getvalue())

        self.ibi_buffer.truncate(0)
        self.ibi_buffer.seek(0)
        self.acc_buffer.truncate(0)
        self.acc_buffer.seek(0)
        self.ecg_buffer.truncate(0)
        self.ecg_buffer.seek(0)
        self.buffer_count = 0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Polar H10 Device Selector")
        self.setGeometry(300, 300, 800, 600)

        self.device_list = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        self.connect_button = QPushButton("Connect")
        self.record_button = QPushButton("Record Data")

        self.ibi_plot = pg.PlotWidget(title='IBI Data')
        self.acc_plot = pg.PlotWidget(title='ACC Data')
        self.ecg_plot = pg.PlotWidget(title='ECG Data')

        layout = QVBoxLayout()
        layout.addWidget(self.device_list)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.record_button)
        layout.addWidget(self.ibi_plot)
        layout.addWidget(self.acc_plot)
        layout.addWidget(self.ecg_plot)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.refresh_button.clicked.connect(self.refresh_devices)
        self.connect_button.clicked.connect(self.connect_device)
        self.record_button.clicked.connect(self.toggle_recording)

        self.scanner = DeviceScanner()
        self.scanner.devices_found.connect(self.update_device_list)

        self.ibi_curve = self.ibi_plot.plot()
        self.acc_curve_x = self.acc_plot.plot(pen='r', name='X')
        self.acc_curve_y = self.acc_plot.plot(pen='g', name='Y')
        self.acc_curve_z = self.acc_plot.plot(pen='b', name='Z')
        self.ecg_curve = self.ecg_plot.plot()

        self.buffer_size = 1000

        self.ibi_data = deque(maxlen=self.buffer_size)
        self.acc_data = deque(maxlen=self.buffer_size)
        self.ecg_data = deque(maxlen=self.buffer_size)

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(50)  # Update every 50ms

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('#'):
            self.toggle_recording()

    @Slot()
    def refresh_devices(self):
        self.device_list.clear()
        self.scanner.start()

    @Slot(list)
    def update_device_list(self, devices):
        self.devices = devices
        for device in devices:
            self.device_list.addItem(f"{device.name} ({device.address})")

    @Slot()
    def connect_device(self):
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a device to connect.")
            return

        selected_index = self.device_list.row(selected_items[0])
        selected_device = self.devices[selected_index]

        self.polar_sensor = PolarH10(selected_device)
        self.sensor_worker = PolarSensorWorker(self.polar_sensor)
        self.sensor_worker.connected.connect(self.on_connected)
        self.sensor_worker.device_info.connect(self.on_device_info)
        self.sensor_worker.ibi_data.connect(self.on_ibi_data)
        self.sensor_worker.acc_data.connect(self.on_acc_data)
        self.sensor_worker.ecg_data.connect(self.on_ecg_data)
        self.sensor_worker.start()

    @Slot()
    def on_connected(self):
        print(f"Connected to {self.polar_sensor}")

    @Slot(str)
    def on_device_info(self, info):
        print(info)

    @Slot(tuple)
    def on_ibi_data(self, data):
        timestamp, ibi_data = data
        self.ibi_data.append((timestamp, ibi_data))

    @Slot(tuple)
    def on_acc_data(self, data):
        timestamp, acc_data = data
        self.acc_data.append((timestamp, acc_data))

    @Slot(tuple)
    def on_ecg_data(self, data):
        timestamp, ecg_data = data
        self.ecg_data.append((timestamp, ecg_data))

    def update_plots(self):
        self.update_ibi_plot()
        self.update_acc_plot()
        self.update_ecg_plot()

    def update_ibi_plot(self):
        if self.ibi_data:
            timestamps, values = zip(*self.ibi_data)
            self.ibi_curve.setData(np.array(timestamps).flatten(), np.array(values).flatten())

    def update_acc_plot(self):
        if self.acc_data:
            timestamps, values = zip(*self.acc_data)
            x_values, y_values, z_values = zip(*values)
            self.acc_curve_x.setData(np.array(timestamps).flatten(), np.array(x_values).flatten())
            self.acc_curve_y.setData(np.array(timestamps).flatten(), np.array(y_values).flatten())
            self.acc_curve_z.setData(np.array(timestamps).flatten(), np.array(z_values).flatten())

    def update_ecg_plot(self):
        if self.ecg_data:
            timestamps, values = zip(*self.ecg_data)
            self.ecg_curve.setData(np.array(timestamps).flatten(), np.array(values).flatten())

    @Slot()
    def toggle_recording(self):
        if hasattr(self, 'sensor_worker'):
            self.sensor_worker.recording_enabled = not self.sensor_worker.recording_enabled
            if self.sensor_worker.recording_enabled:
                self.record_button.setText("Stop Recording")
                self.sensor_worker.recording_folder = self.create_recording_folder()
                self.initialize_csv_files()
                print("Recording started")
            else:
                self.record_button.setText("Record Data")
                self.sensor_worker.flush_buffers()
                print("Recording stopped")

    def create_recording_folder(self):
        base_folder = os.path.dirname(sys.executable)
        date_str = datetime.now().strftime("%d_%m_%Y")
        session_number = 1
        
        existing_folders = [f for f in os.listdir(base_folder) if f.startswith(date_str)]
        if existing_folders:
            session_numbers = [int(f.split('_')[-1]) for f in existing_folders]
            highest_session = max(session_numbers)
            folder_name = f"{date_str}_session_{highest_session}"
            full_path = os.path.join(base_folder, folder_name)
            
            files_to_check = ['polar_ibi_data.csv', 'polar_acc_data.csv', 'polar_ecg_data.csv']
            existing_files = [f for f in files_to_check if os.path.exists(os.path.join(full_path, f))]
            
            if len(existing_files) == 3:
                session_number = highest_session + 1
            elif len(existing_files) > 0:
                session_number = highest_session + 1
            else:
                return full_path
        
        while True:
            folder_name = f"{date_str}_session_{session_number}"
            full_path = os.path.join(base_folder, folder_name)
            if not os.path.exists(full_path):
                os.makedirs(full_path)
                return full_path
            session_number += 1

    def initialize_csv_files(self):
        with open(os.path.join(self.sensor_worker.recording_folder, 'polar_ibi_data.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'IBI'])
        with open(os.path.join(self.sensor_worker.recording_folder, 'polar_acc_data.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'X', 'Y', 'Z'])
        with open(os.path.join(self.sensor_worker.recording_folder, 'polar_ecg_data.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'ECG'])

    def closeEvent(self, event):
        if hasattr(self, 'sensor_worker'):
            self.sensor_worker.stop()
            self.sensor_worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
