from __future__ import annotations

import math
import unittest

import numpy as np

from .barge_wave_sensitivity import fft_frequency_grid, spectrum_component_amplitudes, synthesize_response


class BargeWaveSensitivityTest(unittest.TestCase):
    def test_synthesis_rms_matches_discrete_spectral_variance(self) -> None:
        sample_count, indices, omega = fft_frequency_grid(600.0, 0.1, 0.2, 2.0)
        _, amplitudes = spectrum_component_amplitudes(omega, 2.0, 8.0, 3.3)
        transfer = np.ones((1, omega.size), dtype=complex)
        phases = np.random.default_rng(202600).uniform(0.0, 2.0 * math.pi, omega.size)
        response = synthesize_response(transfer, amplitudes, phases, indices, sample_count)[0]
        expected_rms = math.sqrt(float(np.sum(0.5 * amplitudes**2)))
        self.assertAlmostEqual(float(np.sqrt(np.mean(response**2))), expected_rms, places=10)

    def test_wave_height_scales_linear_response(self) -> None:
        sample_count, indices, omega = fft_frequency_grid(120.0, 0.1, 0.2, 2.0)
        _, amplitudes_1 = spectrum_component_amplitudes(omega, 1.0, 8.0, 3.3)
        _, amplitudes_3 = spectrum_component_amplitudes(omega, 3.0, 8.0, 3.3)
        transfer = np.ones((1, omega.size), dtype=complex)
        phases = np.random.default_rng(7).uniform(0.0, 2.0 * math.pi, omega.size)
        response_1 = synthesize_response(transfer, amplitudes_1, phases, indices, sample_count)
        response_3 = synthesize_response(transfer, amplitudes_3, phases, indices, sample_count)
        np.testing.assert_allclose(response_3, 3.0 * response_1, rtol=1.0e-12, atol=1.0e-12)


if __name__ == "__main__":
    unittest.main()

