import numpy as np
import random
from midiutil import MIDIFile
from typing import Literal
import os

# ---- LSTM-style sequence generator (simplified, no PyTorch needed) ----
# For a real LSTM, you'd train on MIDI data. This demonstrates the logic cleanly.

FOCUS_MODE_NOTES = [60, 62, 64, 65, 67, 69]    # C major pentatonic (calm)
SOCIAL_MODE_NOTES = [60, 63, 65, 67, 70, 72, 75]  # C minor blues (energetic)

def lstm_generate_sequence(seed_notes, mode="focus", length=16):
    """
    Simulates LSTM-style autoregressive note generation.
    In production: replace with trained LSTM model.
    """
    sequence = list(seed_notes[:3])  # seed with first 3 notes
    
    for _ in range(length - 3):
        # LSTM-like: next note influenced by previous context
        context = sequence[-3:]
        avg = np.mean(context)
        
        if mode == "focus":
            # Prefer notes close to current (smooth, ambient)
            candidates = [n for n in FOCUS_MODE_NOTES if abs(n - avg) < 5]
            if not candidates:
                candidates = FOCUS_MODE_NOTES
            next_note = random.choice(candidates)
        else:
            # Social: allow more jumps (energetic)
            weights = [1 / (abs(n - avg) + 1) for n in SOCIAL_MODE_NOTES]
            weights = [w ** 0.3 for w in weights]  # flatten for variety
            total = sum(weights)
            weights = [w / total for w in weights]
            next_note = np.random.choice(SOCIAL_MODE_NOTES, p=weights)
        
        sequence.append(int(next_note))
    
    return sequence

def generate_music(
    room_state: Literal["focus", "social", "energetic", "calm"] = "focus",
    output_path: str = "output.mid",
    duration_seconds: int = 10
):
    """Generate a 10-second MIDI melody based on room state."""
    
    midi = MIDIFile(1)
    track, channel = 0, 0
    tempo = 60 if room_state in ["focus", "calm"] else 120
    
    midi.addTempo(track, 0, tempo)
    
    beats_per_second = tempo / 60
    total_beats = int(duration_seconds * beats_per_second)
    
    if room_state in ["focus", "calm"]:
        # LSTM: slow, low-frequency ambient loop
        notes = lstm_generate_sequence(FOCUS_MODE_NOTES, mode="focus", length=total_beats)
        note_duration = 1.0      # whole beats = slow
        volume = 60              # quiet
        instrument = 89          # Pad 2 (warm) - ambient
    else:
        # Transformer-inspired: high-tempo energetic melody
        notes = lstm_generate_sequence(SOCIAL_MODE_NOTES, mode="social", length=total_beats * 2)
        note_duration = 0.5      # eighth notes = fast
        volume = 100             # loud
        instrument = 81          # Lead 1 (square) - energetic
    
    midi.addProgramChange(track, channel, 0, instrument)
    
    time = 0
    for note in notes:
        midi.addNote(track, channel, note, time, note_duration, volume)
        time += note_duration
        if time >= total_beats:
            break
    
    with open(output_path, "wb") as f:
        midi.writeFile(f)
    
    print(f"✅ Generated {duration_seconds}s MIDI: {output_path} | Mode: {room_state} | Tempo: {tempo} BPM")
    return output_path

if __name__ == "__main__":
    generate_music("focus", "focus_mode.mid")
    generate_music("social", "social_mode.mid")
    generate_music("energetic", "energetic_mode.mid")
    print("All music files generated!")