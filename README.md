# RF Signal Spectrum Analyzer

## Project Overview
A software-based RF signal spectrum analysis project using C++ and Python. The system generates simulated signals, analyzes frequency-spectrum data, detects signal peaks, and visualizes results.

## Features
- Simulated signal generation using C++
- Frequency-spectrum analysis
- Signal peak detection using configurable thresholds
- Strong, Medium, and Weak signal classification
- Frequency-range filtering
- Spectrum visualization using Matplotlib
- CSV exports and text analysis reports
- Automated unit testing with Python unittest

## Technologies Used
- C++
- Python
- NumPy / Matplotlib (as used in the project)
- CSV
- Python unittest

## Sample Results
The current simulation includes signals at:
- 100 Hz — amplitude approximately 1.00
- 200 Hz — amplitude approximately 0.50

The analyzer successfully detected both signals using the default threshold in the tested configuration.

## Generated Files
- `frequency_spectrum.png` — spectrum visualization
- `peak_report.txt` — analysis report
- `detected_signals.csv` — detected signal peaks
- `filtered_signals.csv` — filtered spectrum data

## Testing
Run the automated tests:

```bash
python -m unittest test_plot_spectrum.py -v
```

Latest test result: 15 tests passed.

## How to Run
1. Compile and run the C++ signal generator.
2. Generate `frequency_spectrum.csv`.
3. Install the Python dependencies required by the script.
4. Run `python plot_spectrum.py`.
5. Follow the prompts to select the frequency range and detection threshold.

## Project Scope
This version analyzes simulated signals. It does not yet receive or measure live RF signals from physical radio hardware.

## Future Improvements
- Support configurable signal frequencies and noise levels
- Add more signal-detection and validation tests
- Integrate an SDR receiver for real RF measurements
