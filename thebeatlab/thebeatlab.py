import os
import json
import pandas as pd
from difflib import get_close_matches
import openai
from pydantic import BaseModel


class RecordStore:
    def __init__(self, overall_csv_file, data_directory='data/'):
        # Load the original CSV file and process it
        self.data_directory = data_directory
        self.data = self.process_csv(overall_csv_file)

    def process_csv(self, overall_csv_file):
        # Load the original CSV file
        df = pd.read_csv(overall_csv_file)

        # Function to safely extract artist and songname
        def extract_artist_and_songname(link):
            try:
                parts = link.split('/')
                if len(parts) > 6:  # Ensure there are enough parts
                    artist = parts[5].replace('-', ' ')
                    songname = parts[6]
                    return artist, songname
                else:
                    return None, None
            except Exception as e:
                return None, None

        # Apply the extraction function to the 'original_link' column
        df['artist'], df['songname'] = zip(*df['original_link'].apply(extract_artist_and_songname))

        # Keep rows where extraction was successful
        df = df.dropna(subset=['artist', 'songname'])

        # Extract section type and filename
        df['sectiontype'] = df['section']
        df['filename'] = df['Downloaded File Name'].apply(lambda x: x.strip())
        df['filepath'] = df['filename'].apply(lambda x: f"{self.data_directory}/{x}" if os.path.isfile(f"{self.data_directory}/{x}") else '')

        # Remove rows where the file does not exist
        df = df[df['filepath'] != '']

        # Return processed DataFrame with only the relevant columns
        return df[['artist', 'songname', 'sectiontype', 'filename']].copy()

    def load_music_data(self, json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8-sig') as file:
                    data = json.load(file)
            except FileNotFoundError:
                print("Error: The file was not found.")
                return None, None, None
            except json.JSONDecodeError:
                print("Error: There was an issue decoding the JSON file.")
                return None, None, None
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return None, None, None

            chords = [Chord(**chord_data) for chord_data in data.get('chords', [])]
            notes = [Note(**note_data) for note_data in data.get('notes', [])]

            key = data.get('keys', [{}])[0]
            scale = key.get('scale')
            tonic = key.get('tonic')

            tempo = data.get('tempos', [{}])[0]
            tempo_beat = tempo.get('beat')
            bpm = tempo.get('bpm')
            swing_factor = tempo.get('swingFactor')
            swing_beat = tempo.get('swingBeat')

            meter = data.get('meters', [{}])[0]
            meter_beat = meter.get('beat')
            num_beats = meter.get('numBeats')
            beat_unit = meter.get('beatUnit')

            time = Time(tempo_beat, bpm, swing_factor, swing_beat, meter_beat, num_beats, beat_unit)
            song = Song(f"{tonic}-{scale}", scale, tonic, chords, time, notes)

            return chords, notes, song

    def find_best_match(self, artist=None, songname=None, sectiontype=None):
        # Prioritize exact matches if all fields are provided
        if artist and songname and sectiontype:
            match = self.data[
                (self.data['artist'] == artist) &
                (self.data['songname'] == songname) &
                (self.data['sectiontype'] == sectiontype)
            ]
            if not match.empty:
                return match.iloc[0]['filename']
        
        # Use difflib to find the closest match if exact match isn't found
        best_artist = get_close_matches(artist, self.data['artist'], n=1, cutoff=0.6) if artist else []
        best_songname = get_close_matches(songname, self.data['songname'], n=1, cutoff=0.6) if songname else []
        best_sectiontype = get_close_matches(sectiontype, self.data['sectiontype'], n=1, cutoff=0.6) if sectiontype else []

        # Try to find the best possible match based on available fields
        match = None
        if best_artist and best_songname and best_sectiontype:
            match = self.data[
                (self.data['artist'] == best_artist[0]) &
                (self.data['songname'] == best_songname[0]) &
                (self.data['sectiontype'] == best_sectiontype[0])
            ]
        elif best_artist and best_songname:
            match = self.data[
                (self.data['artist'] == best_artist[0]) &
                (self.data['songname'] == best_songname[0])
            ]
        elif best_artist and best_sectiontype:
            match = self.data[
                (self.data['artist'] == best_artist[0]) &
                (self.data['sectiontype'] == best_sectiontype[0])
            ]
        elif best_songname and best_sectiontype:
            match = self.data[
                (self.data['songname'] == best_songname[0]) &
                (self.data['sectiontype'] == best_sectiontype[0])
            ]
        elif best_artist:
            match = self.data[self.data['artist'] == best_artist[0]]
        elif best_songname:
            match = self.data[self.data['songname'] == best_songname[0]]
        elif best_sectiontype:
            match = self.data[self.data['sectiontype'] == best_sectiontype[0]]

        if match is not None and not match.empty:
            return match.iloc[0]['filename']  # Return the filename of the best match
        return None

    def get_song(self, artist=None, songname=None, sectiontype=None):
        # Get the best match for the provided artist, songname, and sectiontype
        filename = self.find_best_match(artist, songname, sectiontype)
        if filename:
            filepath = f"{self.data_directory}/{filename}"
            chords, notes, song = self.load_music_data(filepath)  # Load the song using the filepath
            return song
        else:
            print("No matching song found.")
            return None

import json
import os

class Song:
    def __init__(self,key,scale,tonic,chords,time,notes,**kwargs):
        # self.absolute_root = self.note_to_midi(key)
        self.key = key
        self.scale = scale
        self.tonic = tonic
        self.time = time
        self.allowed_keys_list = self.generated_keys_list()
        print(self.allowed_keys_list)
        self.chords = chords
        self.notes = notes
        self.generated_absolute_chords()
        self.generated_absolute_notes()
        
    def generated_keys_list(self):
        oct_start = 0
        oct_end = 10
        get_key_shift = self.get_key_shift(self.scale)
        absolute_root = self.note_to_midi(self.tonic, octave=oct_start)
        first_octave = [x + absolute_root for x in get_key_shift]
        key_list = [x + (12 * i) for i in range(oct_end) for x in first_octave]
        return key_list
    def generated_absolute_notes(self):
        if len(self.notes) == 0: return 
        for c in self.notes:
            if not c.isRest:
                absolute_note = self.sd_to_midi(c.sd,c.octave) 
                # print(absolute_note)
                c.absolute_note_position.append(absolute_note)
            
    def generated_absolute_chords(self):
        if len(self.chords) == 0: return 
        for c in self.chords:
            absolute_root = self.note_to_midi(self.tonic) 
            root_abs_position = self.allowed_keys_list.index(absolute_root) + c.root - 1 
            c.absolute_chord_position = [self.allowed_keys_list[root_abs_position],self.allowed_keys_list[root_abs_position+2],self.allowed_keys_list[root_abs_position+4]]
    
    def sd_to_midi(self, sd, octave):
        root_note = self.note_to_midi(self.tonic)
        middle_octave_root = (root_note % 12) + 60
        root_note_abs_position = self.allowed_keys_list.index(middle_octave_root)
        
        # Check if the sd starts with '#' and adjust base_sd accordingly
        issharp = sd[0] == '#'
        isflat = sd[0] == 'b'
        sd = int(sd[1:]) if issharp or isflat else int(sd)
        
        # Calculate the base note in the scale
        note = self.allowed_keys_list[root_note_abs_position + sd - 1] + int(issharp) - int(isflat) + (octave * 12) # Add a semitone (1 MIDI value) if sharp
        
        return note

    def get_key_shift(self, mode):
        ks = {
            "major" : [0, 2, 4, 5, 7, 9, 11],
            "minor" : [0, 2, 3, 5, 7, 8, 10],
            "dorian" : [0, 2, 3, 5, 7, 9, 10],
            "locrian" : [0, 1, 3, 5, 6, 8, 10],
            "mixolydian" : [0, 2, 4, 5, 7, 9, 10],
            "harmonicMinor" : [0, 2, 3, 5, 7, 8, 11],
            "lydian" : [0, 2, 4, 6, 7, 9, 11],
            "phrygian" : [0, 1, 3, 5, 7, 8, 10],
            "phrygianDominant" : [0, 1, 3, 5, 7, 8, 9]
        }
        return ks[mode]
    def note_to_midi(self, note, octave=4):
        notes = {
            'C': 0,
            'Db': 1,
            'C#': 1,
            'D': 2,
            'Eb': 3,
            'D#': 3,
            'E': 4,
            'F': 5,
            'Gb': 6,
            'F#': 6,
            'G': 7,
            'Ab': 8,
            'G#': 8,
            'A': 9,
            'Bb': 10,
            'A#': 10,
            'B': 11
        }
        return notes[note] + (octave * 12)
    def __str__(self):
        return f"key: {self.scale} \t {self.tonic}"
    def __repr__(self):
        return f"key: {self.scale} \t {self.tonic}"

class Time:
    def __init__(self, tempo_beat, bpm, swing_factor, swing_beat, meter_beat, num_beats, beat_unit):
        self.tempo = tempo_beat
        self.bpm = bpm
        self.swing_factor = swing_factor
        self.swing_beat = swing_beat
        self.meter_beat = meter_beat
        self.num_beats = num_beats
        self.beat_unit = beat_unit
        
class Chord:
    def __init__(self, root, beat, duration, type, inversion, applied, adds, omits, alterations, suspensions, substitutions, pedal, alternate, borrowed, isRest, recordingEndBeat=None):
        self.root = root
        self.beat = beat
        self.duration = duration
        self.type = type
        self.inversion = inversion
        self.applied = applied
        self.adds = adds
        self.omits = omits
        self.alterations = alterations
        self.suspensions = suspensions
        self.substitutions = substitutions
        self.pedal = pedal
        self.alternate = alternate
        self.borrowed = borrowed
        self.isRest = isRest
        self.recordingEndBeat = recordingEndBeat
        self.absolute_chord_position = []
    def __repr__(self):
        roman_numerals = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        roman = roman_numerals.get(self.root, '?')
        return f"({roman} : {self.beat}-{self.beat + self.duration - 1})"
    def __str__(self):
        roman_numerals = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII'}
        roman = roman_numerals.get(self.root, '?')
        return f"({roman} : {self.beat}-{self.beat + self.duration - 1})"

class Note:
    def __init__(self, sd, octave, beat, duration, isRest=None, **kwargs):
        self.sd = sd
        self.octave = octave
        self.beat = beat
        self.duration = duration
        self.isRest = isRest
        self.absolute_note_position = []
    def __str__(self):
        return f"({self.sd}-{self.octave}: {self.beat}-{self.beat + self.duration - 0.5})"
    def __repr__(self):
        return f"({self.sd}-{self.octave}: {self.beat}-{self.beat + self.duration - 0.5})"


import pretty_midi
import IPython.display
class Player:
    def __init__(self, bpm=85, instrument_program=42, velocity=100):
        self.velocity = velocity
        # Initialize PrettyMIDI with a default BPM
        self.pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        # Initialize the instrument and add it to PrettyMIDI
        self.instrument = pretty_midi.Instrument(program=instrument_program, is_drum=False, name='piano')
        self.pm.instruments.append(self.instrument)
        self.song = None

    def load_song(self, song):
        self.song = song
        # Update the tempo based on the song's Time object
        self._process_song()

    def _process_song(self):
        self._add_chords_to_instrument()
        self._add_notes_to_instrument()
        self.pm.initial_tempo = self.song.time.bpm

    def _beat_to_seconds(self, beat):
        # Convert beat to seconds considering the tempo, meter, and swing factor
        seconds_per_beat = (60 / self.song.time.bpm)
        
        # Adjust for swing: If the current beat is a swing beat, modify timing
        if beat % self.song.time.swing_beat == 0:
            seconds_per_beat *= (1 + self.song.time.swing_factor)
        else:
            seconds_per_beat *= (1 - self.song.time.swing_factor)
        
        return seconds_per_beat * beat

    def _add_chords_to_instrument(self):
        for c in self.song.chords:
            start_time = self._beat_to_seconds(c.beat)
            end_time = self._beat_to_seconds(c.beat + c.duration)
            
            # Add each note in the chord to the instrument
            for pitch in c.absolute_chord_position:
                self.instrument.notes.append(pretty_midi.Note(self.velocity, pitch, start_time, end_time))

    def _add_notes_to_instrument(self):
        for c in self.song.notes:
            start_time = self._beat_to_seconds(c.beat)
            end_time = self._beat_to_seconds(c.beat + c.duration)
            if len(c.absolute_note_position) > 0:
                self.instrument.notes.append(pretty_midi.Note(self.velocity - 40, c.absolute_note_position[0], start_time, end_time))  # Notes quieter

    def play_piano(self, fs=16000):
        return IPython.display.Audio(self.pm.synthesize(fs=fs), rate=fs)


#Define your structured output model
class SongRequest(BaseModel):
    artist: str
    songname: str
    sectiontype: str

class DJ:
    def __init__(self, record_store: RecordStore, authenticate=False, api_key_file='openaikey.txt'):
        self.record_store = record_store
        self.player = None
        if authenticate:
            self.authenticate(api_key_file)

    def authenticate(self, api_key_file: str):
        # Read the API key from the file
        with open(api_key_file, 'r') as file:
            api_key = file.read().strip()  # Read and strip any surrounding whitespace/newlines
        
        # Export the API key as an environment variable
        os.environ['OPENAI_API_KEY'] = api_key
        openai.api_key = api_key  # Set the API key for the OpenAI client

        # Optionally, print a message to confirm that the key has been set
        print("OpenAI API key has been set and authenticated.")

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

