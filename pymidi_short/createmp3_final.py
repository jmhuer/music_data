import pyaudio
import wave
import numpy as np
import time 
import whisper
import openai
import mido
import time
import ast



chords = {
   "CMajor": [60, 64, 67],          # C, E, G
    "CMinor": [60, 63, 67],          # C, Eb, G
    "DMajor": [62, 66, 69],          # D, F#, A
    "DMinor": [62, 65, 69],          # D, F, A
    "EMajor": [64, 68, 71],          # E, G#, B
    "EMinor": [64, 67, 71],          # E, G, B
    "FMajor": [65, 69, 72],          # F, A, C
    "FMinor": [65, 68, 72],          # F, Ab, C
    "GMajor": [67, 71, 74],          # G, B, D
    "Gmajor": [67, 71, 74],          # G, B, D
    "GMinor": [67, 70, 74],          # G, Bb, D
    "AMajor": [69, 73, 76],          # A, C#, E
    "AMinor": [69, 72, 76],          # A, C, E
    "BMajor": [71, 75, 78],          # B, D#, F#
    "BMinor": [71, 74, 78],          # B, D, F#
    "DbMajor": [61, 65, 68],         # Db, F, Ab
    "DbMinor": [61, 64, 68],         # Db, E, Ab
    "EbMajor": [63, 67, 70],         # Eb, G, Bb
    "EbMinor": [63, 66, 70],         # Eb, Gb, Bb
    "AbMajor": [68, 72, 75],         # Ab, C, Eb
    "AbMinor": [68, 71, 75],         # Ab, B, Eb
    "BbMajor": [70, 74, 77],         # Bb, D, F
    "BbMinor": [70, 73, 77],         # Bb, Db, F
    "CMajor7": [60, 64, 67, 71],     # C, E, G, B
    "CMinor7": [60, 63, 67, 70],     # C, Eb, G, Bb
    "DMajor7": [62, 66, 69, 73],     # D, F#, A, C#
    "DMinor7": [62, 65, 69, 72],     # D, F, A, C
    "EMajor7": [64, 68, 71, 75],     # E, G#, B, D#
    "EMinor7": [64, 67, 71, 74],     # E, G, B, D
    "FMajor7": [65, 69, 72, 76],     # F, A, C, E
    "FMinor7": [65, 68, 72, 75],  
    "GMajor7": [67, 71, 74, 78],     # G, B, D, F#
    "GMinor7": [67, 70, 74, 77],      # G, Bb, D, F
    "GbMajor7": [66, 70, 73, 77],    # Gb, Bb, Db, F
    "BbMinor7": [70, 73, 77, 81],     # Bb, Db, F, Ab,
    "EbMajor7": [63, 67, 70, 74],     # Eb, G, Bb, D
    "AMajor7": [69, 73, 76, 80]     # A, C#, E, G#
}


def play_chord(outport, chord_notes, sleep):
    # Open the MIDI output
    # Send the note on messages
    for note in chord_notes:
        msg = mido.Message('note_on', note=note, velocity=127)
        outport.send(msg)

    # Wait for a bit
    time.sleep(sleep)

    # Send the note off messages
    for note in chord_notes:
        msg = mido.Message('note_off', note=note)
        outport.send(msg)


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



def extract_list_from_string(string):
    try:
        # Find the substring within the string that represents the list
        start = string.index("[")
        end = string.rindex("]")
        list_str = string[start:end+1]

        # Parse the list string into an actual list using the ast module
        extracted_list = ast.literal_eval(list_str)

        return extracted_list
    except (ValueError, SyntaxError):
        # Return None if the string does not contain a valid list
        return None


def calculate_frame_energy(frame):
    # Convert frame to numpy array and calculate energy
    samples = np.frombuffer(frame, dtype=np.int16)
    energy = np.sum(np.abs(samples)) / len(samples)
    return energy

def query_cahtgpt(new_msg):
    openai.api_key = "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"

    messages = [{"role": "system", "content": "You are a helpful assistant. I will be providing you with user request. In your response please provide me with a list of chords the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7"}]
    messages.append({"role": "user", "content": new_msg})
        # doc is here https://platform.openai.com/docs/guides/chat/chat-vs-completions?utm_medium=email&_hsmi=248334739&utm_content=248334739&utm_source=hs_email
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0301", messages=messages)
    # get the reply
    reply = chat_completion.choices[0].message.content
    return reply


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

def open_stream(sample_format, channels, sample_rate, chunk, input_device_index):
    # Close current stream and open a new one
    p = pyaudio.PyAudio()
    return p.open(format=sample_format,
                  channels=channels,
                  rate=sample_rate,
                  input=True,
                  frames_per_buffer=chunk,
                  input_device_index=input_device_index), p

def process_audio(frames, model, sample_rate, chunk):
    # Calculate the number of frames that make up 30 seconds of audio
    frames_per_30_sec = 30 * sample_rate // chunk

    texts = []  # Array to store text results for each chunk
    for i in range(0, len(frames), frames_per_30_sec):
        chunk_frames = frames[i: i + frames_per_30_sec]
        
        # Convert the chunk of frames to audio
        audio = np.frombuffer(b"".join(chunk_frames), np.int16).flatten().astype(np.float32) / 32768.0    

        # Adjust the audio to the expected length
        audio = whisper.pad_or_trim(audio)

        # Convert the audio to a log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # Decode the audio with the whisper model
        options = whisper.DecodingOptions(fp16 = False,language='en')
        result = whisper.decode(model, mel, options)

        # Append the recognized text for the chunk to the list
        texts.append(result.text)

    # Combine all text results into a single string
    text = " ".join(texts)
    return text

def note_length_in_seconds(bpm, time_signature, note_length):
    beats_per_measure, beat_unit = map(int, time_signature.split('/'))
    note_beats = beat_unit / int(note_length.split('/')[1])

    seconds_per_beat = 60.0 / bpm

    return note_beats * seconds_per_beat


def record_audio(filename, input_device_index, save_last_audio=False):
    outport = mido.open_output('USB Midi ')
    model = whisper.load_model("tiny")

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    sample_rate = 16000

    stream, p = open_stream(sample_format, channels, sample_rate, chunk, input_device_index)

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
                text = process_audio(frames, model, sample_rate, chunk)
                print(f"\nRecognized text: \n {text} \n\n")
                
                p.terminate()

                ##chord logic 
                # test_msg = "I want a chord progression in the scale of C that sounds happy"
                request = f"Here is the user request: {text} . In your response please provide me with a list of chords in the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7. PLease follow the form I privided with brakets [.......] with 8 items in the list. Also make sure the chord strings are exactly as written with quotes to specify a string in python. Only use chords I mentioned"

                output = query_cahtgpt(request)
                l = extract_list_from_string(output)
                # print(f"🤖: {output}")

                bpm = 60
                time_signature = "4/4"
                note_length="1/8"
                # time.sleep(0.5)
                time_sleep = note_length_in_seconds(bpm=bpm, time_signature=time_signature, note_length=note_length)
                time_sleep = 1
                for chord in l:
                    print("Playing chord:", chord)
                    print("sleep: ", time_sleep)
                    play_chord(outport, chords[chord], sleep=time_sleep)


                ##




                stream, p = open_stream(sample_format, channels, sample_rate, chunk, input_device_index)

                frames = []
                energy_values = []
                is_ready_to_record = False
                is_recording = False

if __name__ == "__main__":
    find_input()
    filename = "output.wav"
    
    record_audio(filename, input_device_index=0, save_last_audio=False)