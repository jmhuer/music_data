from musiclang.library import *
from musiclang import Score

# Some random bar of chopin op18 Waltz
score = ((V % III.b.M)(
    piano__0=s0 + s2.e.mp + s3.e.mp, 
    piano__4=s0.e.o(-2).p + r.e + s0.ed.o(-1).mp + r.s, 
    piano__5=r + s4.ed.o(-1).mp + r.s, 
    piano__6=r + s6.ed.o(-1).mp + r.s)+ 
(V['7'] % III.b.M)(
    piano__0=s2.ed.mp + r.s, 
    piano__2=s4.ed.mp + r.s, 
    piano__4=s6.ed.o(-1).mp + r.s, 
    piano__5=s0.ed.o(-1).mp + r.s, 
    piano__6=s4.ed.o(-1).mp + r.s))

# Predict the next two chords of the score using huggingface musiclang model
predicted_score = score.predict_score(n_chords=2, temperature=0.5)
# Save it to midi
predicted_score.to_midi('whyyyyyyyyyyy.mid')

