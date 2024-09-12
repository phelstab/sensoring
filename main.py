import sys
import multiprocessing
from PySide6.QtWidgets import QApplication

def run_empatica():
    from Empatica.empatica import MainWindow as EmpaticaWindow
    app = QApplication(sys.argv)
    window = EmpaticaWindow()
    window.show()
    sys.exit(app.exec())

def run_polar():
    from Polar.PolarH10app import MainWindow as PolarWindow
    app = QApplication(sys.argv)
    window = PolarWindow()
    window.show()
    sys.exit(app.exec())

def run_kinect():
    import qdarktheme
    from pykinect_recorder.main_window import MainWindow as KinectWindow
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    screen_size = app.primaryScreen().size()
    width, height = screen_size.width(), screen_size.height()
    main_window = KinectWindow(width, height)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    processes = []
    
    empatica_process = multiprocessing.Process(target=run_empatica)
    polar_process = multiprocessing.Process(target=run_polar)
    kinect_process = multiprocessing.Process(target=run_kinect)
    
    processes.extend([empatica_process, polar_process, kinect_process])
    
    for process in processes:
        process.start()
    
    for process in processes:
        process.join()
