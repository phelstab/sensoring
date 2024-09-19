python version: 3.11

Build a executable file of the program
pyinstaller --clean --onefile --add-data "pykinect_recorder;pykinect_recorder" .\main.py
pyinstaller --onefile --add-data "PolarH10.py;." PolarH10app.py

Video Codec of the .mkv:
Metadata:
    title           : Azure Kinect
    encoder         : libmatroska-1.4.9
    creation_time   : 2024-08-07T10:10:34.000000Z
    K4A_DEPTH_DELAY_NS: 0
    K4A_WIRED_SYNC_MODE: STANDALONE
    K4A_COLOR_FIRMWARE_VERSION: 1.6.110
    K4A_DEPTH_FIRMWARE_VERSION: 1.6.79
    K4A_DEVICE_SERIAL_NUMBER: 001119204312
    K4A_START_OFFSET_NS: 200011000
  Duration: 00:10:04.87, start: 0.000000, bitrate: 858482 kb/s
  Stream #0:0(eng): Video: rawvideo (BGRA / 0x41524742), bgra, 1280x720, SAR 1:1 DAR 16:9, 30 fps, 30 tbr, 1000k tbn (default)
    Metadata:
      title           : COLOR
      K4A_COLOR_TRACK : 810226436614735475
      K4A_COLOR_MODE  : BGRA_720P
  Stream #0:1(eng): Video: rawvideo (b16g / 0x67363162), gray16be, 640x576, SAR 1:1 DAR 10:9, 30 fps, 30 tbr, 1000k tbn (default)
    Metadata:
      title           : DEPTH
      K4A_DEPTH_TRACK : 714354825252198240
      K4A_DEPTH_MODE  : NFOV_UNBINNED
  Stream #0:2(eng): Video: rawvideo (b16g / 0x67363162), gray16be, 640x576, SAR 1:1 DAR 10:9, 30 fps, 30 tbr, 1000k tbn (default)
    Metadata:
      title           : IR
      K4A_IR_TRACK    : 1148602440146072152
      K4A_IR_MODE     : ACTIVE
  Stream #0:3(eng): Subtitle: none (default)
    Metadata:
      title           : IMU
      K4A_IMU_TRACK   : 1118258977371131949
      K4A_IMU_MODE    : ON
  Stream #0:4: Attachment: none
    Metadata:
      filename        : calibration.json
      mimetype        : application/octet-stream
      K4A_CALIBRATION_FILE: calibration.json
Stream mapping:
  Stream #0:0 -> #0:0 (rawvideo (native) -> h264 (libx264))
Press [q] to stop, [?] for help
[libx264 @ 00000202832afdc0] using SAR=1/1
[libx264 @ 00000202832afdc0] using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX FMA3 BMI2 AVX2
[libx264 @ 00000202832afdc0] profile High 4:4:4 Predictive, level 3.1, 4:4:4, 8-bit
[libx264 @ 00000202832afdc0] 264 - core 164 r3161M a354f11 - H.264/MPEG-4 AVC codec - Copyleft 2003-2023 - http://www.videolan.org/x264.html - options: cabac=1 ref=3 deblock=1:0:0 analyse=0x3:0x113 me=hex subme=7 psy=1 psy_rd=1.00:0.00 mixed_ref=1 me_range=16 chroma_me=1 trellis=1 8x8dct=1 cqm=0 deadzone=21,11 fast_pskip=1 chroma_qp_offset=4 threads=12 lookahead_threads=2 sliced_threads=0 nr=0 decimate=1 interlaced=0 bluray_compat=0 constrained_intra=0 bframes=3 b_pyramid=2 b_adapt=1 b_bias=0 direct=1 weightb=1 open_gop=0 weightp=2 keyint=250 keyint_min=25 scenecut=40 intra_refresh=0 rc_lookahead=40 rc=crf mbtree=1 crf=23.0 qcomp=0.60 qpmin=0 qpmax=69 qpstep=4 ip_ratio=1.40 aq=1:1.00
Output #0, mp4, to 'output.mp4':
  Metadata:
    title           : Azure Kinect
    K4A_DEVICE_SERIAL_NUMBER: 001119204312
    K4A_START_OFFSET_NS: 200011000
    K4A_DEPTH_DELAY_NS: 0
    K4A_WIRED_SYNC_MODE: STANDALONE
    K4A_COLOR_FIRMWARE_VERSION: 1.6.110
    K4A_DEPTH_FIRMWARE_VERSION: 1.6.79
    encoder         : Lavf60.16.100
  Stream #0:0(eng): Video: h264 (avc1 / 0x31637661), yuv444p(tv, progressive), 1280x720 [SAR 1:1 DAR 16:9], q=2-31, 30 fps, 15360 tbn (default)
    Metadata:
      title           : COLOR
      K4A_COLOR_TRACK : 810226436614735475
      K4A_COLOR_MODE  : BGRA_720P
      encoder         : Lavc60.31.102 libx264
    Side data:
      cpb: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: N/A


To Mp4:
ffmpeg -i 2024_08_07_12_10_33.mkv -c:v libx264 -crf 23 -preset medium -c:a copy output.mp4

Kinect:
important: the device must be plugged to a USB3.0 port


What is the mkv file format that is exported?
https://learn.microsoft.com/de-de/previous-versions/azure/kinect-dk/record-file-format



Body Tracking Problems:

Initializing body tracking library from C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll
Loading body tracker library from C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll
Body tracker library loaded successfully
Initializing body tracking library from C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll
Loading body tracker library from C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll
Body tracker library loaded successfully
Traceback (most recent call last):
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\renderer\components\viewer_sensors.py", line 109, in select_option
    self.streaming()
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\renderer\components\viewer_sensors.py", line 115, in streaming
    self.play()
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\renderer\components\viewer_sensors.py", line 139, in play
    self.viewer = RecordSensors(device=self.device, video_file_path=self.filename_video, audio_file_path=self.filename_audio)
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\renderer\components\record_sensors.py", line 28, in __init__
    self.body_tracker = start_body_tracker(calibration=device.calibration)
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\pykinect.py", line 78, in start_body_tracker
    return Tracker(calibration, model_type)
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\k4abt\tracker.py", line 12, in __init__
    self._handle = self.create(model_type)
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\k4abt\tracker.py", line 75, in create
    _k4abt.k4abt_tracker_create(self.calibration.handle(), tracker_config, tracker_handle),
  File "C:\Users\lambda\Workspace\sensoring\venv\lib\site-packages\pykinect_azure\k4abt\_k4abt.py", line 54, in k4abt_tracker_create
    _k4abt_tracker_create = k4abt_dll.k4abt_tracker_create
AttributeError: 'NoneType' object has no attribute 'k4abt_tracker_create'
[2024-09-20 00:14:29.957] [critical] [t=10676] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\usbcommand\usbcommand.c (366): find_libusb_device(). libusb device(s) are all unavalable. Is the device being used by another application?
[2024-09-20 00:14:29.957] [error] [t=10676] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\depth_mcu\depth_mcu.c (68): usb_cmd_create(USB_DEVICE_DEPTH_PROCESSOR, device_index, NULL, &depthmcu->usb_cmd) returned failure in depthmcu_create()
[2024-09-20 00:14:29.957] [error] [t=10676] D:\a\1\s\extern\Azure-Kinect-Sensor-SDK\src\sdk\k4a.c (133): depthmcu_create(index, &device->depthmcu) returned failure in k4a_device_open()
Open K4A Device failed!
Exception ignored in: <function Tracker.__del__ at 0x000002C4CD354700>
Traceback (most recent call last):
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\k4abt\tracker.py", line 16, in __del__
    self.destroy()
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\k4abt\tracker.py", line 28, in destroy
    if self.is_valid():
  File "C:\Users\lambda\Workspace\sensoring\Kinect\pykinect_recorder\pyk4a\k4abt\tracker.py", line 19, in is_valid
    return self._handle
AttributeError: 'Tracker' object has no attribute '_handle'