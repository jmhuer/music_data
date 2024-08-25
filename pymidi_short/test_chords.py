import mido
import time

# Open the MIDI output
outport = mido.open_output('USB Midi ')


for i in range(3):
    # Define the notes for the C Major chord
    chord_notes = [60+i, 64+i, 67+i]  # C, E, G in MIDI note numbers
    print("playing chord " , chord_notes)
    # Send the note on messages
    for note in chord_notes:
        msg = mido.Message('note_on', note=note, velocity=127)
        outport.send(msg)

    # Wait for a bit
    time.sleep(2)

    # Send the note off messages
    for note in chord_notes:
        msg = mido.Message('note_off', note=note)
        outport.send(msg)