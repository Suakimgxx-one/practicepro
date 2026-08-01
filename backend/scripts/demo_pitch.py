"""
Demo script: aligns two real audio files and compares their pitch,
printing flagged (out-of-tune) regions.

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

    print(f"Loading reference: {reference_path}")
    reference_waveform, reference_sr = load_audio(reference_path)

    print(f"Loading student:   {student_path}")
    student_waveform, student_sr = load_audio(student_path)

    print("\nAligning performances...")
    alignment = align(reference_waveform, reference_sr, student_waveform, student_sr)

    print("Extracting pitch contours...")
    reference_pitch = extract_pitch_contour(reference_waveform, reference_sr)
    student_pitch = extract_pitch_contour(student_waveform, student_sr)

    print("Comparing pitch at aligned moments...")
    result = compare_pitch(reference_pitch, student_pitch, alignment)

    print(f"\nCompared {len(result.points)} voiced moments.")
    print(f"Mean absolute pitch deviation: {result.mean_absolute_cents_deviation:.1f} cents")

    regions = result.flagged_regions(threshold_cents=25.0)
    if regions:
        print(f"\nFlagged out-of-tune regions (>25 cents off), in reference time:")
        for start, end in regions:
            print(f"  {start:6.2f}s - {end:6.2f}s")
    else:
        print("\nNo regions exceeded the 25-cent flagging threshold.")


if __name__ == "__main__":
    main()
