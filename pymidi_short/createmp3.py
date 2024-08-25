import pyaudio
import wave
import numpy as np
import time 
import whisper
import openai

def find_input():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_index(i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_index(i).get('name'))
    p.terminate()



def query_cahtgpt(new_msg):
    openai.api_key = "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"

    messages = [{"role": "system", "content": "You are a helpful assistant. I will be providing you with user request. In your response please provide me with a list of chords the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7"}]
    messages.append({"role": "user", "content": new_msg})
        # doc is here https://platform.openai.com/docs/guides/chat/chat-vs-completions?utm_medium=email&_hsmi=248334739&utm_content=248334739&utm_source=hs_email
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-0301", messages=messages)
    # get the reply
    reply = chat_completion.choices[0].message.content
    return reply


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

def record_audio(filename, input_device_index):
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
    i = 0 
    while True:
        data = stream.read(chunk)

        energy = calculate_frame_energy(data)
        energy_values.append(energy)

        if len(energy_values) > mute_duration_threshold:
            energy_values.pop(0)

        if not is_ready_to_record and check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
            is_ready_to_record = True
            print("Ready to record - unmute to start")
            # energy_values = []
        
        elif is_ready_to_record and not is_recording and not check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
            is_recording = True
            print("Recording started. Mute to stop recording")
            energy_values = []

        elif is_recording:
            print("Saving audio...")
            frames.append(data)
            if check_mute_consistency(energy_values, mute_threshold, mute_duration_threshold):
                print("Finished recording.")

                stream.stop_stream()
                stream.close()
                p.terminate()

                ##if you want to save uncomment the below
                # wf = wave.open("output" + str(i) + ".wav", "wb")
                # wf.setnchannels(channels)
                # wf.setsampwidth(p.get_sample_size(sample_format))
                # wf.setframerate(sample_rate)
                # wf.writeframes(b"".join(frames))
                # wf.close()
                # i+=1


                # load audio and pad/trim it to fit 30 seconds

                audio = np.frombuffer(b"".join(frames), np.int16).flatten().astype(np.float32) / 32768.0    

                # audio = whisper.load_audio("output" + str(i) + ".wav")
                # audio = whisper.pad_or_trim(audio)

                # make log-Mel spectrogram and move to the same device as the model
                mel = whisper.log_mel_spectrogram(audio).to(model.device)

                # # detect the spoken language
                # _, probs = model.detect_language(mel)
                # print(f"Detected language: {max(probs, key=probs.get)}")

                # decode the audio
                options = whisper.DecodingOptions(fp16 = False,language='en')
                result = whisper.decode(model, mel, options)

                # print the recognized text
                print(result.text)

                
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

if __name__ == "__main__":
    find_input()
    filename = "output.wav"
    msg = "I want a chord progression in the scale of C that sounds mysterius and omnious"
    request = f"please break down the following user request {msg} in your response please provide me with a list of chords in the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7"

    output = query_cahtgpt(request)
    print(f"🤖: {output}")

    # record_audio(filename, input_device_index = 0)
