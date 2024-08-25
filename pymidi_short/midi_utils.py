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
    "CMajor7": [60, 64, 67, 71],     # C, E, G, B
    "CMinor7": [60, 63, 67, 70],     # C, Eb, G, Bb
    "DMajor7": [62, 66, 69, 73],     # D, F#, A, C#
    "DMinor7": [62, 65, 69, 72],     # D, F, A, C
    "EMajor7": [64, 68, 71, 75],     # E, G#, B, D#
    "EMinor7": [64, 67, 71, 74],     # E, G, B, D
    "FMajor7": [65, 69, 72, 76],     # F, A, C, E
    "FMinor7": [65, 68, 72, 75],     # F, Ab, C, Eb
    "GMajor7": [67, 71, 74, 78],     # G, B, D, F#
    "GMinor7": [67, 70, 74, 77]      # G, Bb, D, F
}


def note_length_in_seconds(bpm, time_signature, note_length):
    beats_per_measure, beat_unit = map(int, time_signature.split('/'))
    note_beats = int(beat_unit / int(note_length.split('/')[1]))

    seconds_per_beat = 60.0 / bpm

    return note_beats * seconds_per_beat



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
    "CMajor7": [60, 64, 67, 71],     # C, E, G, B
    "CMinor7": [60, 63, 67, 70],     # C, Eb, G, Bb
    "DMajor7": [62, 66, 69, 73],     # D, F#, A, C#
    "DMinor7": [62, 65, 69, 72],     # D, F, A, C
    "EMajor7": [64, 68, 71, 75],     # E, G#, B, D#
    "EMinor7": [64, 67, 71, 74],     # E, G, B, D
    "FMajor7": [65, 69, 72, 76],     # F, A, C, E
    "FMinor7": [65, 68, 72, 75],     # F, Ab, C, Eb
    "GMajor7": [67, 71, 74, 78],     # G, B, D, F#
    "GMinor7": [67, 70, 74, 77]      # G, Bb, D, F
}


f"please break down the following user request {msg} in your response please provide me with a list of chords in the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7"

"I will be providing you with user request. In your response please provide me with a list of chords the form for example: [\"CMajor\",\"CMajor\", \"AMinor\",\"AMinor\", \"FMajor\",\"FMajor\", \"GMajor\",\"GMajor\"] every chord in the list represents a 1/8th note. Here are all the possible chords you can use: CMajor, CMinor, DMajor, DMinor, EMajor, EMinor, FMajor, FMinor, GMajor, GMinor, AMajor, AMinor, BMajor, BMinor, DbMajor, DbMinor, EbMajor, EbMinor, AbMajor, AbMinor, CMajor7, CMinor7, DMajor7, DMinor7, EMajor7, EMinor7, FMajor7, FMinor7, GMajor7, GMinor7"
