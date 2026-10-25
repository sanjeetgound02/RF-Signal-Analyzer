
import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


# --------------------------------
# 1. File paths
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent

spectrum_file = BASE_DIR / "frequency_spectrum.csv"
report_file = BASE_DIR / "peak_report.txt"
csv_report_file = BASE_DIR / "detected_signals.csv"
filtered_csv_file = BASE_DIR / "filtered_signals.csv"
graph_file = BASE_DIR / "frequency_spectrum.png"


# --------------------------------
# 2. Signal classification
# --------------------------------
def classify_signal(amplitude):
    if amplitude >= 0.8:
        return "Strong Signal"
    elif amplitude >= 0.3:
        return "Medium Signal"
    return "Weak Signal"


# --------------------------------
# 3. Main analyzer
# --------------------------------
def main():
    # Frequency range input
    try:
        min_frequency = float(
            input("Enter minimum frequency (Hz): ")
        )
        max_frequency = float(
            input("Enter maximum frequency (Hz): ")
        )

        if (
            not math.isfinite(min_frequency)
            or not math.isfinite(max_frequency)
            or min_frequency < 0
            or max_frequency <= min_frequency
        ):
            print("Invalid frequency range.")
            return

    except (ValueError, OverflowError):
        print("Please enter valid numeric frequencies.")
        return

    # Read CSV data
    frequencies = []
    amplitudes = []

    try:
        with spectrum_file.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            required = {"Frequency_Hz", "Amplitude"}

            if (
                not reader.fieldnames
                or not required.issubset(reader.fieldnames)
            ):
                print(
                    "CSV must contain Frequency_Hz and Amplitude."
                )
                return

            for row in reader:
                frequency = float(row["Frequency_Hz"])
                amplitude = float(row["Amplitude"])

                if (
                    not math.isfinite(frequency)
                    or not math.isfinite(amplitude)
                    or frequency < 0
                    or amplitude < 0
                ):
                    print("CSV contains invalid numeric data.")
                    return

                frequencies.append(frequency)
                amplitudes.append(amplitude)

    except FileNotFoundError:
        print("ERROR: frequency_spectrum.csv was not found.")
        return
    except (ValueError, KeyError, TypeError, OverflowError) as error:
        print(f"ERROR reading CSV: {error}")
        return
    except OSError as error:
        print(f"ERROR opening CSV: {error}")
        return

    if len(amplitudes) < 3:
        print("At least 3 data points are required.")
        return

    # IMPORTANT: reject unsorted and duplicate frequencies
    if any(
        frequencies[i] <= frequencies[i - 1]
        for i in range(1, len(frequencies))
    ):
        print(
            "ERROR: CSV frequency values must be strictly "
            "ascending with no duplicate frequencies."
        )
        return

    print(f"Loaded frequency data points: {len(amplitudes)}")

    # Estimate noise
    noise_level = statistics.median(amplitudes)
    print(f"Estimated spectrum noise level: {noise_level:.4f}")

    # Detection threshold input
    try:
        threshold_input = input(
            "Enter detection threshold "
            "(press Enter for automatic): "
        ).strip()

        if threshold_input:
            threshold = float(threshold_input)

            if not math.isfinite(threshold) or threshold <= 0:
                print("Threshold must be a positive number.")
                return
        else:
            threshold = max(0.15, noise_level * 4)

    except (ValueError, OverflowError):
        print("Please enter a valid numeric threshold.")
        return

    print(f"Detection threshold: {threshold:.3f}")

    # --------------------------------
    # 4. Detect peaks
    # --------------------------------
    peaks = []

    for i in range(1, len(amplitudes) - 1):
        is_peak = (
            amplitudes[i] > amplitudes[i - 1]
            and amplitudes[i] >= amplitudes[i + 1]
        )

        if is_peak and amplitudes[i] > threshold:
            peaks.append((frequencies[i], amplitudes[i]))

    peaks.sort(key=lambda item: item[1], reverse=True)
    top_peaks = peaks[:10]

    print("\nAll detected signals (top 10)")
    print("------------------------------")

    for frequency, amplitude in top_peaks:
        print(
            f"{frequency:.2f} Hz | "
            f"Amplitude: {amplitude:.3f} | "
            f"Type: {classify_signal(amplitude)}"
        )

    # --------------------------------
    # 5. Filter frequency range
    # --------------------------------
    filtered_data = [
        (frequency, amplitude)
        for frequency, amplitude in zip(frequencies, amplitudes)
        if min_frequency <= frequency <= max_frequency
    ]

    if not filtered_data:
        print("No data in the selected frequency range.")
        return

    filtered_frequencies = [item[0] for item in filtered_data]
    filtered_amplitudes = [item[1] for item in filtered_data]

    visible_peaks = [
        (frequency, amplitude)
        for frequency, amplitude in peaks
        if min_frequency <= frequency <= max_frequency
    ]

    strong_count = sum(
        classify_signal(a) == "Strong Signal"
        for _, a in visible_peaks
    )
    medium_count = sum(
        classify_signal(a) == "Medium Signal"
        for _, a in visible_peaks
    )
    weak_count = sum(
        classify_signal(a) == "Weak Signal"
        for _, a in visible_peaks
    )

    print("\nSelected Range Signal Summary")
    print("------------------------------")
    print(f"Total detected signals: {len(visible_peaks)}")
    print(f"Strong signals: {strong_count}")
    print(f"Medium signals: {medium_count}")
    print(f"Weak signals: {weak_count}")
    print(f"Selected range: {min_frequency}-{max_frequency} Hz")
    print(f"Filtered data points: {len(filtered_data)}")

    # --------------------------------
    # 6. Strongest peak and noise ratio
    # --------------------------------
    strongest_frequency = None
    strongest_amplitude = None
    peak_to_noise_db = None

    if visible_peaks:
        strongest_frequency, strongest_amplitude = max(
            visible_peaks, key=lambda item: item[1]
        )

        print(
            f"\nStrongest peak: {strongest_frequency:.2f} Hz"
        )
        print(f"Peak amplitude: {strongest_amplitude:.4f}")

        if noise_level > 0 and strongest_amplitude > 0:
            peak_to_noise_db = 20 * math.log10(
                strongest_amplitude / noise_level
            )
            print(
                f"Approx. peak-to-noise ratio: "
                f"{peak_to_noise_db:.2f} dB"
            )
    else:
        print("\nNo peaks detected in selected range.")

    # --------------------------------
    # 7. Save graph
    # --------------------------------
    try:
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            filtered_frequencies,
            filtered_amplitudes,
            linewidth=1,
            label="Filtered Spectrum"
        )

        ax.axhline(
            y=threshold,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"Detection Threshold: {threshold:.3f}"
        )

        for frequency, amplitude in visible_peaks:
            ax.scatter(frequency, amplitude, s=45)
            ax.annotate(
                f"{frequency:.0f} Hz",
                (frequency, amplitude),
                xytext=(4, 8),
                textcoords="offset points"
            )

        ax.set_title("RF Spectrum - Peak Detection")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_xlim(min_frequency, max_frequency)
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(graph_file, dpi=150)
        plt.close(fig)

        print(f"\nGraph saved to: {graph_file.resolve()}")

    except (OSError, ValueError) as error:
        print(f"WARNING: Graph could not be saved: {error}")
        plt.close("all")

    # --------------------------------
    # 8. Save text report
    # --------------------------------
    try:
        with report_file.open("w", encoding="utf-8") as report:
            report.write("RF Signal Analyzer - Analysis Report\n")
            report.write("====================================\n\n")
            report.write(
                f"Selected frequency range: "
                f"{min_frequency}-{max_frequency} Hz\n"
            )
            report.write(
                f"Total spectrum data points: {len(amplitudes)}\n"
            )
            report.write(
                f"Filtered data points: {len(filtered_data)}\n"
            )
            report.write(
                f"Noise estimate (full spectrum): "
                f"{noise_level:.4f}\n"
            )
            report.write(f"Detection threshold: {threshold:.3f}\n")
            report.write(
                f"Detected peaks in selected range: "
                f"{len(visible_peaks)}\n\n"
            )

            report.write("Signal Summary:\n")
            report.write("------------------------------\n")
            report.write(f"Strong signals: {strong_count}\n")
            report.write(f"Medium signals: {medium_count}\n")
            report.write(f"Weak signals: {weak_count}\n\n")

            report.write(
                "Frequency (Hz) | Amplitude | Classification\n"
            )
            report.write(
                "--------------------------------------------\n"
            )

            for frequency, amplitude in visible_peaks:
                report.write(
                    f"{frequency:14.2f} | "
                    f"{amplitude:9.4f} | "
                    f"{classify_signal(amplitude)}\n"
                )

            if strongest_frequency is not None:
                report.write(
                    "\nStrongest peak in selected range:\n"
                )
                report.write(
                    f"Frequency: {strongest_frequency:.2f} Hz\n"
                )
                report.write(
                    f"Amplitude: {strongest_amplitude:.4f}\n"
                )

                if peak_to_noise_db is not None:
                    report.write(
                        f"Approx. peak-to-noise ratio: "
                        f"{peak_to_noise_db:.2f} dB\n"
                    )
            else:
                report.write(
                    "\nNo peaks detected in selected range.\n"
                )

        print(f"Analysis report saved to: {report_file.resolve()}")

    except OSError as error:
        print(f"ERROR saving report: {error}")

    # --------------------------------
    # 9. Export CSV files
    # --------------------------------
    def export_csv(path, rows):
        with path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "Frequency_Hz",
                "Amplitude",
                "Signal_Classification"
            ])

            for frequency, amplitude in rows:
                writer.writerow([
                    f"{frequency:.2f}",
                    f"{amplitude:.4f}",
                    classify_signal(amplitude)
                ])

        print(f"CSV saved to: {path.resolve()}")

    try:
        export_csv(csv_report_file, top_peaks)
    except OSError as error:
        print(f"ERROR saving detected_signals.csv: {error}")

    try:
        export_csv(filtered_csv_file, visible_peaks)
    except OSError as error:
        print(f"ERROR saving filtered_signals.csv: {error}")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
