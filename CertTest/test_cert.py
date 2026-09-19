import unittest
import os
import glob
import math


REL_TOL = 1.0e-1
ABS_TOL = 1.0e-7

def isfloat(instr):
    try:
        _ = float(instr)
        return True
    except:
        return False

    
class TestCertRegression(unittest.TestCase):
    def compare_cert(self, cert):
        start_dir = os.path.dirname( os.path.realpath(__file__) )
        print(f'Running regression tests for {cert} example')
        truth_dir = os.path.join(start_dir, cert, 'Output_Benchmark')
        actual_dir = os.path.join(start_dir, cert, 'Output')
        all_files = glob.glob(os.path.join(truth_dir, '**', '*.*'), recursive=True)
        all_files = sorted(os.path.relpath(path, truth_dir) for path in all_files)

        self.assertTrue(all_files, f'No benchmark files found for {cert}')
        for relative_file in all_files:
            truth_file = os.path.join(truth_dir, relative_file)
            actual_file = os.path.join(actual_dir, relative_file)
            with self.subTest(cert=cert, file=relative_file):
                self.assertTrue(os.path.exists(actual_file), f'Missing output file: {actual_file}')
                with open(truth_file) as handle:
                    truth_data = handle.read().splitlines()
                with open(actual_file) as handle:
                    actual_data = handle.read().splitlines()

                self.assertEqual(len(truth_data), len(actual_data), f'Line count differs for {relative_file}')
                mismatches = []
                for line_index, (truth_line, actual_line) in enumerate(zip(truth_data, actual_data), start=1):
                    truth_tokens = truth_line.split()
                    actual_tokens = actual_line.split()
                    if len(truth_tokens) != len(actual_tokens):
                        mismatches.append(
                            f'line {line_index}: token count {len(truth_tokens)} vs {len(actual_tokens)}'
                        )
                        continue
                    for token_index, (truth_token, actual_token) in enumerate(zip(truth_tokens, actual_tokens), start=1):
                        truth_is_float = isfloat(truth_token)
                        actual_is_float = isfloat(actual_token)
                        if truth_is_float and actual_is_float:
                            truth_value = float(truth_token)
                            actual_value = float(actual_token)
                            if math.isnan(truth_value) or math.isnan(actual_value):
                                if math.isnan(truth_value) and math.isnan(actual_value):
                                    continue
                                mismatches.append(
                                    f'line {line_index}, token {token_index}: '
                                    f'TRUTH {truth_value} vs NEW {actual_value}'
                                )
                                continue
                            if math.isinf(truth_value) or math.isinf(actual_value):
                                if truth_value == actual_value:
                                    continue
                                mismatches.append(
                                    f'line {line_index}, token {token_index}: '
                                    f'TRUTH {truth_value} vs NEW {actual_value}'
                                )
                                continue
                            if not math.isclose(
                                truth_value,
                                actual_value,
                                rel_tol=REL_TOL,
                                abs_tol=ABS_TOL,
                            ):
                                mismatches.append(
                                    f'line {line_index}, token {token_index}: '
                                    f'TRUTH {truth_value} vs NEW {actual_value}'
                                )
                        elif truth_is_float != actual_is_float:
                            mismatches.append(
                                f'line {line_index}, token {token_index}: '
                                f'numeric/text mismatch {truth_token!r} vs {actual_token!r}'
                            )
                        elif truth_token != actual_token:
                            mismatches.append(
                                f'line {line_index}, token {token_index}: '
                                f'{truth_token!r} vs {actual_token!r}'
                            )
                self.assertFalse(
                    mismatches,
                    f'{len(mismatches)} mismatch(es) in {relative_file}; first: {mismatches[0] if mismatches else ""}',
                )

    def test_cylinder(self):
        self.compare_cert('Cylinder')

    def test_deepcwind(self):
        self.compare_cert('DeepCwind')

    def test_hywind_spar(self):
        self.compare_cert('HywindSpar')

    def test_moonpool(self):
        self.compare_cert('Moonpool')

def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestCertRegression)


if __name__ == "__main__":
    result = unittest.TextTestRunner().run(suite())

    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
