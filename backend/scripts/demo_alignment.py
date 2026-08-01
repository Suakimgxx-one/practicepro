"""
Demo script: aligns two real audio files and prints the resulting
timestamp mapping.

Usage (from inside the api container):
    PYTHONPATH=. python3 scripts/demo_alignment.py <reference_audio_path> <student_audio_path>
"""
import sys

from analysis_engine.alignment import align
from analysis_engine.features import load_audio


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <reference_path> <student_path>")
        sys.exit(1)

    reference_path, student_path = sys.argv[1], sys.argv[2]

    print(f"Loading reference: {reference_path}")
    reference_waveform, reference_sr = load_audio(reference_path)
    print(f"  -> {len(reference_waveform) / reference_sr:.2f}s at {reference_sr}Hz")

    print(f"Loading student:   {student_path}")
    student_waveform, student_sr = load_audio(student_path)
    print(f"  -> {len(student_waveform) / student_sr:.2f}s at {student_sr}Hz")

    print("\nRunning DTW alignment...")
    result = align(reference_waveform, reference_sr, student_waveform, student_sr)

    print(f"\nTotal alignment cost: {result.cost:.2f} (lower = more similar note sequences)")

    reference_duration = len(reference_waveform) / reference_sr
    print("\nSample mapping (reference time -> corresponding student time):")
    print(f"{'ref_time':>10} -> {'student_time':>12}")

    step = max(reference_duration / 20, 0.5)
    t = 0.0
    while t <= reference_duration:
        mapped = result.reference_to_student(t)
        print(f"{t:>9.2f}s -> {mapped:>11.2f}s")
        t += step


if __name__ == "__main__":
    main()
