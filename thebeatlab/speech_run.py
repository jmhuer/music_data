import os
import wave
import numpy as np
import whisper
import openai
import simpleaudio as sa
from pydantic import BaseModel
import threading
import numpy as np
from .thebeatlab import Chord, Note, Song, RecordStore, Player, DJ
from . import alsa_suppress  # This suppresses ALSA warnings globally
import pyaudio  # Your existing PyAudio imports and initialization
import torch
from scipy.signal import resample

class SpeechDJ:
    def __init__(self, overall_csv_file, authenticate=False, api_key_file='openaikey.txt', downsample_rate=16000):
        self.chunk = 2048 * 2
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 44100
        self.downsample_rate = downsample_rate  # The target downsample rate
        self.mute_threshold = 5
        self.mute_duration_threshold = 10

        self.model = whisper.load_model("base")
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
            print("Model moved to GPU.")
        else:
            print("CUDA is not available. Model is running on CPU.")
        
        self.record_store = RecordStore(overall_csv_file)
        self.dj = DJ(self.record_store, authenticate=authenticate, api_key_file=api_key_file)
        self.p = pyaudio.PyAudio()

        self.current_playback_thread = None  # Track the current playback thread
        self.current_play_obj = None  # Track the current PlayObject
        self.record_store = RecordStore(overall_csv_file)  # Initialize the RecordStore
        self.dj = DJ(self.record_store, authenticate=authenticate, api_key_file=api_key_file)  # Initialize the DJ
        self.p = pyaudio.PyAudio()  # Initialize PyAudio

    def authenticate(self, api_key_file: str):
        with open(api_key_file, 'r') as file:
            api_key = file.read().strip()
        os.environ['OPENAI_API_KEY'] = api_key
        openai.api_key = api_key
        print("OpenAI API key has been set and authenticated.")

    def find_input(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if self.p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                print("Input Device id ", i, " - ", self.p.get_device_info_by_index(i).get('name'))

    def calculate_frame_energy(self, frame):
        samples = np.frombuffer(frame, dtype=np.int16)
        energy = np.sum(np.abs(samples)) / len(samples)
        return energy

    def check_mute_consistency(self, energy_values):
        if len(energy_values) < self.mute_duration_threshold:
            return False
        reference_energy = energy_values[0]
        for i in range(1, self.mute_duration_threshold):
            if abs(energy_values[i] - reference_energy) > self.mute_threshold:
                return False
        return True

    def save_audio(self, filename, frames):
        wf = wave.open(filename, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()

    def process_audio(self, frames):
        frames_per_30_sec = 30 * self.sample_rate // self.chunk
        texts = []
        for i in range(0, len(frames), frames_per_30_sec):
            chunk_frames = frames[i: i + frames_per_30_sec]
            audio = np.frombuffer(b"".join(chunk_frames), np.int16).flatten().astype(np.float32) / 32768.0
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            options = whisper.DecodingOptions(fp16=False, language='en')
            result = whisper.decode(self.model, mel, options)
            texts.append(result.text)
        return " ".join(texts)
    def open_stream(self, input_device_index):
        return self.p.open(format=self.sample_format,
                           channels=self.channels,
                           rate=self.sample_rate,
                           input=True,
                           frames_per_buffer=self.chunk,
                           input_device_index=input_device_index)

    def downsample_audio(self, frames, filename="downsampled_audio.wav"):
        # Combine all frames into a single numpy array
        audio_data = np.hstack([np.frombuffer(frame, dtype=np.int16) for frame in frames])
        
        # Downsample the audio to the target rate
        number_of_samples = round(len(audio_data) * float(self.downsample_rate) / self.sample_rate)
        downsampled_audio_data = resample(audio_data, number_of_samples).astype(np.int16)
        
        # Save the downsampled audio to a file
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # Assuming 16-bit audio
            wf.setframerate(self.downsample_rate)
            wf.writeframes(downsampled_audio_data.tobytes())

        print(f"Downsampled audio saved to {filename}")
        
         # Print statements to confirm values
        print(f"Original sample rate: {self.sample_rate} Hz")
        print(f"Target downsample rate: {self.downsample_rate} Hz")
        print(f"Original number of samples: {len(audio_data)}")
        print(f"Downsampled number of samples: {len(downsampled_audio_data)}")
        print(f"First 10 samples of original audio: {audio_data[:10]}")
        print(f"First 10 samples of downsampled audio: {downsampled_audio_data[:10]}")

        
        return downsampled_audio_data

    def process_audio_downsample(self, frames):
        downsampled_audio_data = self.downsample_audio(frames)
        
        # Use a 30-second chunk size for processing at the downsampled rate
        chunk_duration_seconds = 30  # 30 seconds
        chunk_size_samples = int(chunk_duration_seconds * self.downsample_rate)
        
        texts = []
        
        for i in range(0, len(downsampled_audio_data), chunk_size_samples):
            chunk_frames = downsampled_audio_data[i: i + chunk_size_samples]
            audio = np.array(chunk_frames).astype(np.float32) / 32768.0
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            options = whisper.DecodingOptions(fp16=False, language='en')
            result = whisper.decode(self.model, mel, options)
            
            if result.text.strip():
                texts.append(result.text)
                print(f"Processed chunk: {result.text}")
                
        return " ".join(texts)


    def play_audio_in_background(self, filename):
        # Stop current playback if any
        if self.current_playback_thread and self.current_playback_thread.is_alive():
            print("Stopping current audio playback before starting new one.")
            self.stop_current_audio_playback()
        
        # Start new playback
        thread = threading.Thread(target=self.play_audio, args=(filename,))
        self.current_playback_thread = thread
        thread.start()
        return thread

    def stop_current_audio_playback(self):
        if self.current_play_obj:
            self.current_play_obj.stop()  # Stop the audio
            self.current_play_obj = None

    def play_audio(self, filename):
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        self.current_play_obj = play_obj  # Store the reference to stop it later
        play_obj.wait_done()  # Wait until playback is finished
        self.current_play_obj = None  # Clear the reference after playback finishes

    def converse(self, filename, input_device_index, save_last_audio=False):
        stream = self.open_stream(input_device_index)
        frames = []
        energy_values = []
        is_ready_to_record = False
        is_recording = False

        while True:
            data = stream.read(self.chunk)
            energy = self.calculate_frame_energy(data)
            energy_values.append(energy)

            if len(energy_values) > self.mute_duration_threshold:
                energy_values.pop(0)

            if not is_ready_to_record and self.check_mute_consistency(energy_values):
                is_ready_to_record = True
                print("Ready to record - unmute to start")

            elif is_ready_to_record and not is_recording and not self.check_mute_consistency(energy_values):
                is_recording = True
                print("Recording started. Mute to stop recording")

            elif is_recording:
                frames.append(data)
                if self.check_mute_consistency(energy_values):
                    if save_last_audio:
                        print("Saving audio...")
                        self.save_audio(filename, frames)
                    print("Finished recording. Processing audio...")
                    

                    # # Downsample the recorded audio
                    # downsampled_audio = self.downsample_audio(frames)
                    # downsampled_frames = [downsampled_audio.tobytes()]

                    # Process the downsampled audio
                    # text = self.process_audio(frames)
                    text = self.process_audio_downsample(frames)
                    print(f"\nRecognized text: \n {text} \n\n")
                    stream.stop_stream()
                    stream.close()

                    # Process the request and get the song
                    song = self.dj.process_request(text)
                    if song:
                        player = Player(bpm=85, instrument_program=42)
                        player.load_song(song)
                        audio = player.play_piano()

                        if audio:
                            # Save the generated audio to a file
                            song_filename = "generated_song.wav"
                            with wave.open(song_filename, "wb") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(self.downsample_rate)  # Save at the downsampled rate
                                wf.writeframes(audio.data)

                            # Play the song in the background while continuing the loop
                            ##BEFORE PLAYING NEW AUDIO  - STOP ANY AUDIO THAT IS CURRENTLY PLAYING IN OTHER THREAD
                            self.play_audio_in_background(song_filename)

                    # Restart stream process
                    stream = self.open_stream(input_device_index)
                    frames = []
                    energy_values = []
                    is_ready_to_record = False
                    is_recording = False

