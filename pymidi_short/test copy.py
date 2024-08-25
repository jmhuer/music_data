import mido
from mido import Message
import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
print(available_ports)


if available_ports:
    midiout.open_port('USB Midi ')

with midiout:
    # This is an example of message, change it according your needs
    # with the MIDI message you get from MidiView
    note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, 60, 0]
    # Here you send the message to the device
    midiout.send_message(note_on)
    time.sleep(0.5)
    # Here you send the stop message
    midiout.send_message(note_off)
    time.sleep(0.1)