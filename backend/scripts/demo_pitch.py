"""
Demo script: aligns two real audio files and compares their pitch.

Usage (from inside the api container):
    PYTHONPATH=. python3 scripts/demo_pitch.py <reference_audio_path> <student_audio_path>
"""
import sys
from analysis_engine.alignment import align
from analysis_engine.features import load_audio
from analysis_engine.pitch import compare_pitch, extract_pitch_contour


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <reference_path> <student_path>")
        sys.exit(1)
    reference_path, student_path = sys.argv[1], sys.argv[2]
    reference_waveform, reference_sr = load_audio(reference_path)
    student_waveform, student_sr = load_audio(student_path)
    alignment = align(reference_waveform, reference_sr, student_waveform, student_sr)
    reference_pitch = extract_pitch_contour(reference_waveform, reference_sr)
    student_pitch = extract_pitch_contour(student_waveform, student_sr)
    result = compare_pitch(reference_pitch, student_pitch, alignment)
    print(f"Compared {len(result.points)} voiced moments.")
    print(f"Mean absolute pitch deviation: {result.mean_absolute_cents_deviation:.1f} cents")
    regions = result.flagged_regions(threshold_cents=25.0)
    for start, end in regions:
        print(f"  {start:6.2f}s - {end:6.2f}s")


if __name__ == "__main__":
    main()
