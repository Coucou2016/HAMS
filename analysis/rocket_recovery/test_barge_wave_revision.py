from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

from .barge_wave_revision import (
    CASE_DIR,
    DEFAULT_MAX_DELTA_OMEGA_RAD_S,
    LEG_LAYOUT_PATH,
    MIN_REALIZATIONS,
    SUPPORTED_DURATIONS_S,
    build_revision_deck_points,
    build_revision_transfer_matrix,
    build_synthesis_frequency_grid,
    bootstrap_quantile_ci,
    fine_frequency_grid,
    interpolate_complex_rao,
    load_existing_leg_layout,
    periodicity_diagnostics,
    response_metrics_batch,
    spectrum_component_amplitudes,
    synthesize_response_on_fine_grid,
)
from .barge_wave_duration_sensitivity import compute_nested_duration_cases


class BargeWaveRevisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads((CASE_DIR / "platform_config.json").read_text(encoding="utf-8"))
        self.deck_rao = json.loads(
            (CASE_DIR / "Output" / "RocketRecovery" / "deck-point-rao.json").read_text(encoding="utf-8")
        )

    def test_bem_axis_and_fine_axis_are_distinct_and_within_limit(self) -> None:
        bem = np.asarray(self.deck_rao["frequencies_rad_s"], dtype=float)
        self.assertEqual(bem.size, 19)
        for duration in SUPPORTED_DURATIONS_S:
            grid = build_synthesis_frequency_grid(bem, duration)
            fine = np.asarray(grid["omega_rad_s"], dtype=float)
            self.assertGreater(fine.size, bem.size)
            self.assertAlmostEqual(float(fine[0]), 0.2)
            self.assertAlmostEqual(float(fine[-1]), 2.0)
            self.assertLessEqual(float(np.max(np.diff(fine))), DEFAULT_MAX_DELTA_OMEGA_RAD_S + 1.0e-10)
            self.assertGreater(float(grid["implied_repeat_period_s"]), duration)

    def test_complex_interpolation_keeps_complex_phase(self) -> None:
        source = np.array([0.2, 0.4])
        values = np.array([1.0 + 0.0j, 0.0 + 1.0j])
        result = interpolate_complex_rao(source, values, np.array([0.3]))
        np.testing.assert_allclose(result, np.array([0.5 + 0.5j]))
        self.assertAlmostEqual(float(np.angle(result[0])), math.pi / 4.0)

    def test_existing_radius_and_azimuths_generate_physical_points_and_keep_generic(self) -> None:
        layout = load_existing_leg_layout(LEG_LAYOUT_PATH)
        point_sets = build_revision_deck_points(self.config, layout)
        physical = point_sets["physical_legs"]
        self.assertEqual([point["id"] for point in physical], ["leg_1", "leg_2", "leg_3", "leg_4"])
        self.assertEqual([point["azimuth_deg"] for point in physical], [45.0, 135.0, 225.0, 315.0])
        for point in physical:
            x, y, z = point["position_m"]
            self.assertAlmostEqual(math.hypot(x, y), 6.926037828369117, places=12)
            self.assertAlmostEqual(z, 3.0)
        generic = {point["id"]: point["position_m"] for point in point_sets["generic_sampling"]}
        self.assertEqual(generic["leg_forward_port"], [9.0, 9.0, 3.0])
        self.assertEqual(generic["leg_aft_starboard"], [-9.0, -9.0, 3.0])
        self.assertEqual(len(point_sets["all"]), 9)

    def test_transfer_velocity_and_angle_rate_use_i_omega_after_interpolation(self) -> None:
        layout = load_existing_leg_layout(LEG_LAYOUT_PATH)
        points = build_revision_deck_points(self.config, layout)["all"]
        omega = fine_frequency_grid(0.2, 2.0, 0.005, 600.0)
        names, transfer = build_revision_transfer_matrix(self.deck_rao, 90.0, omega, points)
        for name in ("landing_center", "leg_1", "leg_4", "leg_forward_port"):
            z_index = names.index(f"{name}.z_m")
            vz_index = names.index(f"{name}.vz_m_s")
            np.testing.assert_allclose(transfer[vz_index], 1j * omega * transfer[z_index])
        roll_index = names.index("platform.roll_rad")
        roll_rate_index = names.index("platform.roll_rate_rad_s")
        np.testing.assert_allclose(transfer[roll_rate_index], 1j * omega * transfer[roll_index])

    def test_fine_grid_synthesis_matches_direct_complex_superposition(self) -> None:
        omega = fine_frequency_grid(0.2, 0.4, 0.02, 20.0)
        amplitudes = np.linspace(0.01, 0.03, omega.size)
        phases = np.linspace(0.1, 1.2, omega.size)
        transfer = np.vstack([np.ones(omega.size, dtype=complex), 0.4 - 0.2j * np.ones(omega.size)])
        time = np.arange(50, dtype=float) * 0.1
        actual = synthesize_response_on_fine_grid(transfer, amplitudes, phases, omega, time, n_fft=65536)
        expected = np.real(
            np.sum(
                transfer[:, :, None]
                * amplitudes[None, :, None]
                * np.exp(1j * phases[None, :, None])
                * np.exp(1j * omega[None, :, None] * time[None, None, :]),
                axis=1,
            )
        )
        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=2.0e-8)

    def test_spectrum_variance_matches_m0_on_fine_grid(self) -> None:
        omega = fine_frequency_grid(0.2, 2.0, 0.005, 600.0)
        density, amplitudes = spectrum_component_amplitudes(omega, 2.0, 8.0, 3.3)
        self.assertAlmostEqual(float(np.trapezoid(density, omega)), 2.0**2 / 16.0, places=14)
        self.assertAlmostEqual(float(np.sum(0.5 * amplitudes**2)), 2.0**2 / 16.0, places=14)

    def test_bootstrap_p95_ci_is_reproducible(self) -> None:
        values = np.arange(1.0, 101.0)
        first = bootstrap_quantile_ci(values, resamples=200, seed=17)
        second = bootstrap_quantile_ci(values, resamples=200, seed=17)
        self.assertEqual(first, second)
        self.assertLessEqual(first["lower"], float(np.quantile(values, 0.95)))
        self.assertGreaterEqual(first["upper"], float(np.quantile(values, 0.95)))
        self.assertEqual(first["resamples"], 200)

    def test_periodicity_check_flags_a_record_that_contains_a_repeat(self) -> None:
        time = np.arange(300, dtype=float) * 0.1
        signal = np.sin(2.0 * math.pi * time / 10.0)
        result = periodicity_diagnostics(signal, 0.1, 10.0, 30.0)
        self.assertFalse(result["pass"])
        self.assertTrue(result["record_covers_repeat_period"])
        self.assertAlmostEqual(float(result["duplicate_period_relative_rms_error"]), 0.0, places=12)
        self.assertGreater(float(result["autocorrelation"]["at_repeat_period"]), 0.99)

    def test_deck_edge_immersion_uses_deck_height_and_mean_free_surface(self) -> None:
        layout = load_existing_leg_layout(LEG_LAYOUT_PATH)
        points = build_revision_deck_points(self.config, layout)["all"]
        point_ids = [point["id"] for point in points]
        names = []
        for point_id in point_ids:
            names.extend([f"{point_id}.z_m", f"{point_id}.vz_m_s"])
        names.extend(
            [
                "platform.roll_rad",
                "platform.pitch_rad",
                "platform.roll_rate_rad_s",
                "platform.pitch_rate_rad_s",
            ]
        )
        response = np.zeros((2, len(names), 4), dtype=float)
        response[1, names.index("landing_center.z_m"), :] = -4.0
        metrics = response_metrics_batch(names, response, ["leg_1", "leg_2", "leg_3", "leg_4"], point_ids, self.config["platform"])
        self.assertAlmostEqual(float(metrics["deck_edge.max_immersion_m"][0]), 0.0)
        self.assertAlmostEqual(float(metrics["deck_edge.max_immersion_m"][1]), 1.0)

    def test_realization_floor_is_explicit(self) -> None:
        self.assertEqual(MIN_REALIZATIONS, 1000)

    def test_duration_sensitivity_uses_nested_prefixes_on_one_grid(self) -> None:
        layout = load_existing_leg_layout(LEG_LAYOUT_PATH)
        point_sets = build_revision_deck_points(self.config, layout)
        deck_points = [point_sets["all"][0], *point_sets["physical_legs"]]
        rows = compute_nested_duration_cases(
            self.config,
            self.deck_rao,
            deck_points,
            ["leg_1", "leg_2", "leg_3", "leg_4"],
            {"id": "test", "hs_m": 1.0, "tp_s": 8.0, "gamma": 3.3},
            90.0,
            (2.0, 4.0, 6.0),
            4,
            17,
            0.5,
            DEFAULT_MAX_DELTA_OMEGA_RAD_S,
            20,
            2,
            5.0,
        )
        self.assertEqual([row["duration_s"] for row in rows], [2.0, 4.0, 6.0])
        grids = [row["frequency_grid"] for row in rows]
        self.assertEqual(len({row["delta_omega_rad_s"] for row in grids}), 1)
        self.assertTrue(all(row["common_grid_across_durations"] for row in grids))
        self.assertTrue(all(row["designed_for_maximum_duration_s"] == 6.0 for row in grids))
        p95 = [row["statistics"]["landing_center.max_abs_vertical_velocity_m_s"]["p95"] for row in rows]
        self.assertLessEqual(p95[0], p95[1] + 1.0e-12)
        self.assertLessEqual(p95[1], p95[2] + 1.0e-12)


if __name__ == "__main__":
    unittest.main()
