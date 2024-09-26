# https://learn.microsoft.com/en-us/azure/ai-services/Speech-Service/speech-devices

# Cant Record audio
# https://learn.microsoft.com/en-us/azure/kinect-dk/azure-kinect-recorder

import pyaudio
import wave

def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []

    for i in range(0, num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        devices.append((i, device_info.get('name')))
    
    p.terminate()
    return devices

def find_kinect_device():
    devices = list_audio_devices()
    for device in devices:
        if "Azure Kinect" in device[1]:
            return device[0]
    return None

def record_audio(device_index, duration=10, output_file="output.wav"):
    p = pyaudio.PyAudio()

    # Open the audio stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=7,  # Azure Kinect DK has a 7-microphone array
                    rate=16000,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024)

    print("Recording...")
    frames = []

    for _ in range(0, int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a file
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(7)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

# Main script
if __name__ == "__main__":
    kinect_device_index = find_kinect_device()
    if kinect_device_index is not None:
        print(f"Azure Kinect DK audio device found: {kinect_device_index}")
        record_audio(kinect_device_index)
    else:
        print("Azure Kinect DK audio device not found.")