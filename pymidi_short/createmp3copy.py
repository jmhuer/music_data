import pyaudio
import wave
import numpy as np

def find_input():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_index(i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))
    p.terminate()


def calculate_frame_energy(frame):
    samples = np.frombuffer(frame, dtype=np.int16)
    energy = np.sum(np.abs(samples)) / len(samples)
    return energy


def check_mute_consistency(energy_values, threshold, consecutive_frames):
    if len(energy_values) < consecutive_frames:
        return False
    reference_energy = energy_values[0]
    for i in range(1, consecutive_frames):
        if abs(energy_values[i] - reference_energy) > threshold:
            return False
    return True


def record_audio(filename, record_seconds, input_device_index):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    sample_rate = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=input_device_index)

    frames = []
    energy_values = []
    mute_threshold = 5  # Adjust the threshold as needed
    mute_duration_threshold = 10  # Adjust the duration as needed

    print("Recording...")
    for _ in range(int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

        energy = calculate_frame_energy(data)
        energy_values.append(energy)

        if len(energy_values) > mute_duration_threshold:
            energy_values.pop(0)

        if check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
            print("Microphone muted. Stopping recording.")
            break

    print("Finished recording.")

    stream.stop_stream()
    stream.close()

    p.terminate()

    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()

if __name__ == "__main__":
    find_input()
    filename = "output.wav"
    record_seconds = 20
    input_device_index = 0
    record_audio(filename, record_seconds, input_device_index)
