# music_data


You can see the json files in data.zip 

To try out playing a json file look at the jupyter notebook: read_songsv3.ipynb
This uses the module "beatlab" that handles all the music processing. Its actually quite simple considering it can basically play any song in any key and tempo. Thats the great thing about this json format 

This is how you interact 

To just play a random song .. notice the input_text = f"Play the song {random_songname}" then dj.process_request processes the text by asking gpt for a structured input. Structure is defined by SongRequest. See code below 




    #Define your structured output model
    class SongRequest(BaseModel):
        artist: str
        songname: str
        sectiontype: str

    def process_request(self, input_text: str) -> Song:
        # System message to instruct the model on how to behave
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful assistant. When given a request for a song, "
                "you should attempt to understand the artist, song name, and section type, "
                "even if the user makes a typo or uses a non-standard name. Correct obvious mistakes "
                "and extract the correct structured data."
            )
        }

        # Define the messages including the system message and user input
        messages = [
            system_message,
            {"role": "user", "content": input_text},
        ]

        # Create an OpenAI client instance
        client = openai.OpenAI()

        # Call the OpenAI API to get structured output
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages,
            response_format=SongRequest,  # Use the Pydantic model directly here
        )

        # Extract the structured response content
        song_request = completion.choices[0].message.parsed

        # Use the extracted information to retrieve the song from the RecordStore
        song = self.record_store.get_song(
            artist=song_request.artist,
            songname=song_request.songname,
            sectiontype=song_request.sectiontype
        )

        if song:
            print("Song object loaded successfully.")
            return song
        else:
            print("No matching song found.")
            return None




Now to run this see code below for how we initialize the classes. overall.csv is the list of songs we have in the data. 
Note there is problem.. the overall.csv is messy and the name of the songs are not well organzied. For example a_team_1_verse.json. So sometiems the song will not be found because the llm is looking for a team and it doesnt match a_team_1_verse. We need to imporve the retrival approach. 

Anyways, see below for how we run from a given input_text



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



This other part here is how you use speach to request a song. But you will need a microphone with a mute button... this is because I didnt want to write code for trigger words. so mute button has a very clear signal that we are no longer listening for input. The speach thing isnt too important for us, but if you want to try it I can ship you a microphone with mute button - I have a few. 

Also "output.wav" is incase you want to save the music the DJ plays. 




    # Initialize the SpeechDJ
    speech_dj = SpeechDJ("overall.csv", authenticate=True)

    # Use the converse method to record audio, process it, and play the song
    speech_dj.converse("output.wav", input_device_index=11, save_last_audio=False)



It uses a local whisper model to process speach. it essentially creates the input_text from speach then processes the song the same way as the example above this one. 

----
Note there is a log of junk in this repo I havent cleaned it up. You will find some code realted to pygeometric because I have ran some experiments around GNNs for music applications. A different project for another day.. 
Also you will also see pymidi_short/ 
This has an SAM application for deploying a LLM wrapper. Ive been using it via telegram. I start a chat with a bot that I can chat with. 



## TODO
- We need a template web LLM chat that will fit out needs [Nithish]
  > Update: <add here>

- We need to finish this code base .. I need to extend functionality to all differrent chords 'types' right now the all chords use the standard chord type. [juan]
  > Update: <add here>

- We need a LLM based appraoch to process the input_text with structure. We need to find a good way to map input_text to actions: play, modify, answer general questions, etc. This might be a prompting thing + some tools to get structured outputs
  > Update: <add here>

- We need to finetune the LLM to understand and generate Json files like the ones used here. This will require finetunning.
  > Update: <add here>

- We need to figure out how the backend will work. I think tone.js can be used to substitude the python code here. But we need to think about the architecture
  > Update: <add here>





