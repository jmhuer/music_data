# music_data


You can see the json files in data.zip 

To try out playing a json file look at the jupyter notebook: read_songsv3.ipynb
This uses the module "beatlab" that handles all the music processing. Its actually quite simple considering it can basically play any song in any key and tempo. Thats the great thing about this json format 


This is how you interact 

To just play a random song .. notice the input_text = f"Play the song {random_songname}" the dj.process request is just a palce holder for when we eventually use a language model to process the request. Right now it just uses some basic regex to extract the song name from the input_text. Note that the regex based extraction of input_text sometimes fucks up. 

'''

    # Initialize the RecordStore
    record_store = RecordStore("overall.csv")

    # Create the DJ instance with authentication
    dj = DJ(record_store, authenticate=True)

    # Generate a random song name from the folder "data/"
    song_folder = "data/"
    song_files = os.listdir(song_folder)
    random_song_file = random.choice(song_files)

    # Remove the "-<number>" suffix and the file extension
    random_songname = re.sub(r"-\d+", "", os.path.splitext(random_song_file)[0])
    print(random_songname)
    # random_songname = "Belle"
    # Example song request
    input_text = f"Play the song {random_songname}"

    # Process the request and get the song
    song = dj.process_request(input_text)
    if song:
        # Assuming song is an instance of the Song class
        player = Player(bpm=85, instrument_program=42)
        player.load_song(song)
        audio = player.play_piano()

        # If running in an environment that supports audio playback, like Jupyter:
        if audio:
            display(audio)
'''


This other part here is how you use speach to request a song. 

'''

    # Initialize the SpeechDJ
    speech_dj = SpeechDJ("overall.csv", authenticate=True)

    # Use the converse method to record audio, process it, and play the song
    speech_dj.converse("output.wav", input_device_index=11, save_last_audio=False)

'''

It uses a local whisper model to process speach. it essentially creates the input_text from speach then processes the song the same way as the example above this one. 


## TODO
- We need a template web LLM chat that will fit out needs [Nithish]
- We need to finish this code base .. I need to extend functionality to all differrent chords 'types' right now the all chords use the standard chord type. [juan]
- We need a LLM based appraoch to process the input_text with structure. We need to find a good way to map input_text to actions: play, modify, answer general questions, etc. This might be a prompting thing + some tools to get structured outputs
- We need to finetune the LLM to understand and generate Json files like the ones used here. This will require finetunning.
- We need to figure out how the backend will work. I think tone.js can be used to substitude the python code here. But we need to think about the architecture 





