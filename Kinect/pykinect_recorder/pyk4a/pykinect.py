import ctypes

from .k4a import _k4a, Device, default_configuration
from .k4arecord import _k4arecord
from .k4arecord.playback import Playback
from .k4abt import _k4abt
from .utils import (
    get_k4a_module_path,
    get_k4abt_module_path,
    get_k4arecord_module_path,
)

# import tracker
from .k4abt.tracker import Tracker

def initialize_libraries(module_k4a_path=None, module_k4abt_path=None, track_body=False) -> bool:
    # Search the module path for k4a if not available
    if module_k4a_path is None:
        module_k4a_path = get_k4a_module_path()

    module_k4arecord_path = get_k4arecord_module_path(module_k4a_path)
    _flag = True
    try:
        # Initialize k4a related wrappers
        init_k4a(module_k4a_path)

        # Initialize k4arecord related wrappers
        init_k4arecord(module_k4arecord_path)

        if track_body:
            # Search the module path for k4abt if not available
            if module_k4abt_path is None:
                module_k4abt_path = get_k4abt_module_path()

            # Initialize k4abt related wrappers
            init_k4abt(module_k4abt_path)
    except:
        print("Can not setting .dll")
        _flag = False

    finally:
        return _flag


def init_k4a(module_k4a_path):
    _k4a.setup_library(module_k4a_path)


def init_k4abt(module_k4abt_path):
    _k4abt.setup_library(module_k4abt_path)


def init_k4arecord(module_k4arecord_path):
    _k4arecord.setup_library(module_k4arecord_path)


def start_device(
    device_index=0,
    config=default_configuration,
    record=False,
    record_filepath="output.mkv",
    audio_filepath="output.wav"
):
    # Create device object
    device = Device(device_index)

    # Start device
    device.start(config, record, record_filepath)

    # Store the audio file path in the device object
    if record:
        device.audio_filepath = audio_filepath

    return device

def start_body_tracker(model_type=_k4abt.K4ABT_DEFAULT_MODEL, calibration=None):
    if calibration:
        return Tracker(calibration, model_type)
    else:
        return Tracker(Device.calibration, model_type)


def start_playback(filepath):
    return Playback(filepath)
