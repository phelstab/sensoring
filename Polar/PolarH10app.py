import asyncio
from bleak import BleakScanner
from PolarH10 import PolarH10
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox
from PySide6.QtCore import QThread, Signal, Slot, QObject

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
    ibi_data = Signal(str)
    acc_data = Signal(str)
    ecg_data = Signal(str)

    def __init__(self, polar_sensor):
        super().__init__()
        self.polar_sensor = polar_sensor

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
                self.ibi_data.emit(f"IBI data: {ibi_data} ms at {timestamp}")

            while not self.polar_sensor.acc_queue_is_empty():
                timestamp, acc_data = self.polar_sensor.dequeue_acc()
                self.acc_data.emit(f"ACC data: {acc_data} at {timestamp}")

            while not self.polar_sensor.ecg_queue_is_empty():
                timestamp, ecg_data = self.polar_sensor.dequeue_ecg()
                self.ecg_data.emit(f"ECG data: {ecg_data} µV at {timestamp}")

            await asyncio.sleep(1)

    def run(self):
        asyncio.run(self.connect_and_start_streams())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Polar H10 Device Selector")
        self.setGeometry(300, 300, 400, 300)

        self.device_list = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        self.connect_button = QPushButton("Connect")

        layout = QVBoxLayout()
        layout.addWidget(self.device_list)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.connect_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.refresh_button.clicked.connect(self.refresh_devices)
        self.connect_button.clicked.connect(self.connect_device)

        self.scanner = DeviceScanner()
        self.scanner.devices_found.connect(self.update_device_list)

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

    @Slot(str)
    def on_ibi_data(self, data):
        print(data)

    @Slot(str)
    def on_acc_data(self, data):
        print(data)

    @Slot(str)
    def on_ecg_data(self, data):
        print(data)

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
