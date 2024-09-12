import asyncio
from bleak import BleakScanner
from PolarH10 import PolarH10
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox
from PySide6.QtCore import QThread, Signal, Slot, QObject
import numpy as np
import pyqtgraph as pg
from collections import deque
import csv
import time
from pynput import keyboard

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
    ibi_data = Signal(tuple)  # Emit tuple (timestamp, ibi_data)
    acc_data = Signal(tuple)  # Emit tuple (timestamp, acc_data)
    ecg_data = Signal(tuple)  # Emit tuple (timestamp, ecg_data)

    def __init__(self, polar_sensor):
        super().__init__()
        self.polar_sensor = polar_sensor
        self.recording_enabled = False

    async def connect_and_start_streams(self):
        await self.polar_sensor.connect()
        self.connected.emit()

        await self.polar_sensor.get_device_info()
        device_info = await self.polar_sensor.print_device_info()
        self.device_info.emit(device_info)

        await self.polar_sensor.start_hr_stream()
        await self.polar_sensor.start_acc_stream()
        await self.polar_sensor.start_ecg_stream()

        while True:
            while not self.polar_sensor.ibi_queue_is_empty():
                timestamp, ibi_data = self.polar_sensor.dequeue_ibi()
                self.ibi_data.emit((timestamp, ibi_data))
                if self.recording_enabled:
                    self.write_to_csv('ibi_data.csv', [timestamp, ibi_data])

            while not self.polar_sensor.acc_queue_is_empty():
                timestamp, acc_data = self.polar_sensor.dequeue_acc()
                self.acc_data.emit((timestamp, acc_data))
                if self.recording_enabled:
                    self.write_to_csv('acc_data.csv', [timestamp] + list(acc_data))

            while not self.polar_sensor.ecg_queue_is_empty():
                timestamp, ecg_data = self.polar_sensor.dequeue_ecg()
                self.ecg_data.emit((timestamp, ecg_data))
                if self.recording_enabled:
                    self.write_to_csv('ecg_data.csv', [timestamp, ecg_data])

            await asyncio.sleep(1)

    def run(self):
        asyncio.run(self.connect_and_start_streams())

    def write_to_csv(self, filename, data):
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

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

        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

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
        self.update_ibi_plot()

    @Slot(tuple)
    def on_acc_data(self, data):
        timestamp, acc_data = data
        self.acc_data.append((timestamp, acc_data))
        self.update_acc_plot()

    @Slot(tuple)
    def on_ecg_data(self, data):
        timestamp, ecg_data = data
        self.ecg_data.append((timestamp, ecg_data))
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
                self.initialize_csv_files()
                print("Recording started")
            else:
                self.record_button.setText("Record Data")
                print("Recording stopped")

    def initialize_csv_files(self):
        with open('polar_ibi_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'IBI'])
        with open('polar_acc_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'X', 'Y', 'Z'])
        with open('polar_ecg_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'ECG'])

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
