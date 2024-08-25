import os
import wave
import numpy as np
import whisper
import openai
import simpleaudio as sa
from pydantic import BaseModel
import threading

from .thebeatlab import Chord, Note, Song, RecordStore, Player, DJ
from . import alsa_suppress  # This suppresses ALSA warnings globally
import pyaudio  # Your existing PyAudio imports and initialization

class SpeechDJ:
    def __init__(self, overall_csv_file, authenticate=False, api_key_file='openaikey.txt'):
        self.chunk = 2048 * 2
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 44100
        self.mute_threshold = 5
        self.mute_duration_threshold = 10

        self.model = whisper.load_model("base")  # Load Whisper model
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

    def open_stream(self, input_device_index):
        return self.p.open(format=self.sample_format,
                           channels=self.channels,
                           rate=self.sample_rate,
                           input=True,
                           frames_per_buffer=self.chunk,
                           input_device_index=input_device_index)

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

    def play_audio_in_background(self, filename):
        # This method starts the audio playback in a separate thread
        thread = threading.Thread(target=self.play_audio, args=(filename,))
        thread.start()
        return thread

    def play_audio(self, filename):
        # Use simpleaudio to play the audio file
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until playback is finished

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
                    text = self.process_audio(frames)
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
                                wf.setframerate(self.sample_rate)
                                wf.writeframes(audio.data)

                            # Play the song in the background while continuing the loop
                            self.play_audio_in_background(song_filename)

                    # Restart stream process
                    stream = self.open_stream(input_device_index)
                    frames = []
                    energy_values = []
                    is_ready_to_record = False
                    is_recording = False
