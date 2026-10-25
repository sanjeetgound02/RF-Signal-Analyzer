
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from plot_spectrum import classify_signal, main


class TestSignalClassification(unittest.TestCase):

    def test_strong_signal(self):
        self.assertEqual(classify_signal(0.8), "Strong Signal")

    def test_medium_signal(self):
        self.assertEqual(classify_signal(0.5), "Medium Signal")

    def test_weak_signal(self):
        self.assertEqual(classify_signal(0.2), "Weak Signal")

    def test_medium_signal_boundary(self):
        self.assertEqual(classify_signal(0.3), "Medium Signal")

    def test_strong_signal_boundary(self):
        self.assertEqual(classify_signal(0.8), "Strong Signal")

    def test_zero_amplitude(self):
        self.assertEqual(classify_signal(0.0), "Weak Signal")

    def test_negative_amplitude(self):
        self.assertEqual(classify_signal(-0.5), "Weak Signal")


class TestFrequencyValidation(unittest.TestCase):

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["-10", "500"])
    def test_negative_minimum_frequency(self, mock_input, mock_print):
        main()
        mock_print.assert_any_call("Invalid frequency range.")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["500", "100"])
    def test_maximum_less_than_minimum(self, mock_input, mock_print):
        main()
        mock_print.assert_any_call("Invalid frequency range.")


class TestCSVValidation(unittest.TestCase):

    def test_invalid_amplitude_in_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Frequency_Hz", "Amplitude"])
                writer.writerow([1, 0.1])
                writer.writerow([2, "invalid"])
                writer.writerow([3, 0.3])

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "10"]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )

            self.assertIn("ERROR reading CSV:", printed_text)

            
    def test_empty_csv_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            # Create an empty CSV file
            csv_path.write_text("", encoding="utf-8")

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "500"]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )


        self.assertTrue(
    "ERROR" in printed_text.upper()
    or "EMPTY" in printed_text.upper()
    or "NO DATA" in printed_text.upper()
    or "CSV MUST CONTAIN FREQUENCY_HZ AND AMPLITUDE" in printed_text.upper(),
    f"Expected an empty-file error. Output:\n{printed_text}"
)


    def test_unsorted_frequency_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Frequency_Hz", "Amplitude"])
                writer.writerow([100, 0.5])
                writer.writerow([50, 0.3])
                writer.writerow([200, 0.8])

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "500"]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )

            self.assertTrue(
                "ERROR" in printed_text.upper()
                or "ASCENDING" in printed_text.upper()
                or "SORT" in printed_text.upper(),
                f"Expected unsorted-frequency validation. Output:\n{printed_text}"
            )


    def test_negative_frequency_in_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Frequency_Hz", "Amplitude"])
                writer.writerow([10, 0.5])
                writer.writerow([-20, 0.3])
                writer.writerow([30, 0.8])

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "500"]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )

            self.assertTrue(
                "ERROR" in printed_text.upper()
                or "NEGATIVE" in printed_text.upper()
                or "INVALID" in printed_text.upper(),
                f"Expected negative-frequency validation. Output:\n{printed_text}"
            )


    def test_duplicate_frequency_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Frequency_Hz", "Amplitude"])
                writer.writerow([100, 0.5])
                writer.writerow([100, 0.7])
                writer.writerow([200, 0.8])

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "500", ""]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )

            # Duplicate frequencies should be rejected if the program
            # requires strictly increasing frequency values.
            self.assertTrue(
                "ERROR" in printed_text.upper()
                or "DUPLICATE" in printed_text.upper()
                or "ASCENDING" in printed_text.upper()
                or "SORT" in printed_text.upper(),
                f"Expected duplicate-frequency validation. Output:\n{printed_text}"
            )


class TestMissingCSVColumns(unittest.TestCase):

    def test_missing_amplitude_column(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "frequency_spectrum.csv"

            with csv_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Frequency_Hz"])
                writer.writerow([100])
                writer.writerow([200])
                writer.writerow([300])

            with patch("plot_spectrum.spectrum_file", csv_path):
                with patch("builtins.input", side_effect=["0", "500"]):
                    with patch("builtins.print") as mock_print:
                        main()

            printed_text = "\n".join(
                " ".join(str(arg) for arg in call.args)
                for call in mock_print.call_args_list
            )

            # The program must report the missing column
            # or reject the invalid CSV data.
            self.assertTrue(
                "ERROR reading CSV:" in printed_text
                or "Amplitude" in printed_text
                or "KeyError" in printed_text,
                f"Missing-column error was not reported. Output:\n{printed_text}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

