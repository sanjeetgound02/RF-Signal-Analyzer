
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <fstream>

using namespace std;

const double PI = 3.14159265358979323846;

int main() {
    const int sampleCount = 1000;
    const double sampleRate = 1000.0;

    vector<double> signal(sampleCount);

    mt19937 generator(42);
    normal_distribution<double> noise(0.0, 0.2);

    // Generate signal containing 100 Hz and 200 Hz
    for (int n = 0; n < sampleCount; n++) {
        double time = n / sampleRate;

        double cleanSignal =
            sin(2 * PI * 100.0 * time)
            + 0.5 * sin(2 * PI * 200.0 * time);

        signal[n] = cleanSignal + noise(generator);
    }

    // Save frequency spectrum data
    ofstream file("frequency_spectrum.csv");

    if (!file.is_open()) {
        cout << "Could not create CSV file." << endl;
        return 1;
    }

    file << "Frequency_Hz,Amplitude\n";
    file << fixed << setprecision(4);

    cout << fixed << setprecision(2);
    cout << "RF Frequency Spectrum Analyzer\n";
    cout << "------------------------------\n";
    cout << "Detected frequency peaks:\n\n";

    // Discrete Fourier Transform (DFT)
    for (int k = 1; k < sampleCount / 2; k++) {
        double realPart = 0.0;
        double imaginaryPart = 0.0;

        for (int n = 0; n < sampleCount; n++) {
            double angle =
                2 * PI * k * n / sampleCount;

            realPart += signal[n] * cos(angle);
            imaginaryPart -= signal[n] * sin(angle);
        }

        double amplitude =
            2.0 * sqrt(realPart * realPart
            + imaginaryPart * imaginaryPart)
            / sampleCount;

        double frequency =
            k * sampleRate / sampleCount;

        file << frequency << "," << amplitude << "\n";

        // Display the two expected frequency peaks
        if (abs(frequency - 100.0) < 0.5 ||
            abs(frequency - 200.0) < 0.5) {
            cout << "Frequency: " << frequency
                 << " Hz | Amplitude: "
                 << amplitude << endl;
        }
    }

    file.close();

    cout << "\nSpectrum saved to frequency_spectrum.csv\n";
    cout << "Analysis completed!\n";

    return 0;
}
