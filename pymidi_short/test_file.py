import mido
import time

time.sleep(2)
# Open the MIDI output
outport = mido.open_output('USB Midi ')

# Load the MIDI file
mid = mido.MidiFile('test2.mid')

# Play the MIDI file
for msg in mid.play():
    outport.send(msg)
    time.sleep(msg.time if msg.time > 0 else 0)
