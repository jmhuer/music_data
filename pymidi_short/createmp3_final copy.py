import pyaudio
import wave
import numpy as np
import time 
import whisper

def find_input():
    # Initialize PyAudio and get device info
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    # Iterate over all devices and print input ones
    for i in range(0, numdevices):
        if (p.get_device_info_by_index(i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))
    p.terminate()


def calculate_frame_energy(frame):
    # Convert frame to numpy array and calculate energy
    samples = np.frombuffer(frame, dtype=np.int16)
    energy = np.sum(np.abs(samples)) / len(samples)
    return energy


def check_mute_consistency(energy_values, threshold, consecutive_frames):
    # Check if energy levels are consistently below threshold for specified number of frames
    if len(energy_values) < consecutive_frames:
        return False
    reference_energy = energy_values[0]
    for i in range(1, consecutive_frames):
        if abs(energy_values[i] - reference_energy) > threshold:
            return False
    return True

def save_audio(filename, sample_format, channels, sample_rate, frames):
    # Save audio to file
    p = pyaudio.PyAudio()
    wf = wave.open(filename, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()

def reopen_stream(p, sample_format, channels, sample_rate, chunk, input_device_index):
    # Close current stream and open a new one
    p.terminate()
    p = pyaudio.PyAudio()
    return p.open(format=sample_format,
                  channels=channels,
                  rate=sample_rate,
                  input=True,
                  frames_per_buffer=chunk,
                  input_device_index=input_device_index), p

def process_audio(frames, model):
    # Process audio: detect language and decode
    audio = np.frombuffer(b"".join(frames), np.int16).flatten().astype(np.float32) / 32768.0    
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(fp16 = False, language='en')
    result = whisper.decode(model, mel, options)
    return result.text

def record_audio(filename, input_device_index, save_last_audio=False):
    model = whisper.load_model("tiny")

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    sample_rate = 16000

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
    is_ready_to_record = False
    is_recording = False

    while True:
        data = stream.read(chunk)

        energy = calculate_frame_energy(data)
        energy_values.append(energy)

        if len(energy_values) > mute_duration_threshold:
            energy_values.pop(0)

        if not is_ready_to_record and check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
            is_ready_to_record = True
            print("Ready to record - unmute to start")
        
        elif is_ready_to_record and not is_recording and not check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
            is_recording = True
            print("Recording started. Mute to stop recording")

        elif is_recording:
            frames.append(data)
            if check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
                if save_last_audio: 
                    print("Saving audio...")
                    save_audio(filename, sample_format, channels, sample_rate, frames)
                print("Finished recording. Processing audio...")
                text = process_audio(frames, model)
                print(f"Recognized text: {text}")
                
                stream, p = reopen_stream(p, sample_format, channels, sample_rate, chunk, input_device_index)

                frames = []
                energy_values = []
                is_ready_to_record = False
                is_recording = False

if __name__ == "__main__":
    find_input()
    filename = "output.wav"
    input_device_index = 0
    record_audio(filename, input_device_index, save_last_audio=False)