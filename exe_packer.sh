cd Empatica
pyinstaller --clean --onefile Empatica.py
cd ../Polar
pyinstaller --clean --onefile --add-data "PolarH10.py;." PolarH10app.py
cd ../Kinect
pyinstaller --clean --onefile --add-data "pykinect_recorder;pykinect_recorder" main.py
cd ..