from __future__ import annotations

import math
import unittest

import numpy as np

from .chrono_revision_study import (
    ACTIVE_DOF_INDICES,
    contact_force_audit,
    default_study_config,
    detect_contact_events,
    interval_average_resample,
    load_platform_operator,
    make_time_grid,
    smooth_contact_components,
    smooth_contact_potential_j,
)


class ChronoRevisionContactLawTest(unittest.TestCase):
    def test_review_triplet_is_not_a_100_mn_per_m_linear_pair(self) -> None:
        audit = contact_force_audit()["review_triplet_check"]
        self.assertAlmostEqual(audit["nominal_linear_force_mn"], 14.8, places=12)
        self.assertAlmostEqual(audit["reported_force_mn"], 2.678, places=12)
        self.assertAlmostEqual(audit["implied_delta_at_100mn_per_m_m"], 0.02678, places=12)
        self.assertFalse(audit["reported_force_reachable_by_current_tanh_damper_at_delta"])

    def test_current_smooth_formula_is_unilateral_and_bounded(self) -> None:
        zero = smooth_contact_components(-0.01, 5.0)
        self.assertEqual(float(zero["force_n"]), 0.0)
        compressed = smooth_contact_components(0.148, 0.0)
        self.assertAlmostEqual(float(compressed["force_n"]), 2_600_000.0 * 0.148, places=6)
        high_rate = smooth_contact_components(0.148, 1.0e6)
        self.assertLessEqual(float(high_rate["force_n"]), 2.0 * 935_000.0)

    def test_hard_stop_potential_is_zero_before_reference_stroke(self) -> None:
        self.assertAlmostEqual(float(smooth_contact_potential_j(0.0)), 0.0, places=12)
        below = float(smooth_contact_potential_j(0.148))
        expected = 0.5 * 2_600_000.0 * 0.148**2
        self.assertAlmostEqual(below, expected, places=9)
        self.assertGreater(float(smooth_contact_potential_j(0.5)), below)


class ChronoRevisionCouplingNumericsTest(unittest.TestCase):
    def test_time_grid_is_exact(self) -> None:
        time = make_time_grid(506.0, 516.0, 0.0005)
        self.assertEqual(len(time), 20_001)
        self.assertEqual(float(time[0]), 506.0)
        self.assertEqual(float(time[-1]), 516.0)
        np.testing.assert_allclose(np.diff(time), 0.0005, rtol=0.0, atol=1.0e-12)

    def test_interval_average_preserves_constant_wrench(self) -> None:
        fine_time = np.linspace(0.0, 1.0, 101)
        values = np.column_stack([np.full(len(fine_time), 3.0), np.full(len(fine_time), -4.0)])
        target_time = np.array([0.0, 0.5, 1.0])
        np.testing.assert_allclose(interval_average_resample(fine_time, values, target_time), [[3.0, -4.0]] * 3)

    def test_event_time_is_interpolated_between_contact_samples(self) -> None:
        time = np.array([0.0, 0.5, 1.0])
        delta = np.array([[-0.2, -0.1], [0.1, -0.1], [0.2, 0.1]])
        events = detect_contact_events(time, delta)
        self.assertAlmostEqual(events["first_contact_time_s"], 0.3333333333333333)
        self.assertAlmostEqual(events["first_contact_time_by_leg_s"]["leg_2"], 0.75)
        self.assertEqual(events["event_count"], 2)

    def test_active_wrench_indices_are_heave_roll_pitch(self) -> None:
        np.testing.assert_array_equal(ACTIVE_DOF_INDICES, np.array([2, 3, 4]))

    def test_platform_operator_uses_one_archived_medium_hydrodynamic_source(self) -> None:
        operator = load_platform_operator(default_study_config())
        audit = operator.audit()
        self.assertEqual(operator.hydrodynamic_source_dir.name, "medium_local025_high5")
        self.assertEqual(len(operator.omega_rad_s), 73)
        self.assertGreater(audit["active_radiation_minimum_eigenvalue_kg_s"], 0.0)
        self.assertEqual(audit["added_mass_infinite_definition"]["mesh_level"], "medium")
        for key in ("added_mass", "radiation_damping", "wave_excitation"):
            self.assertIn("medium_local025_high5", audit["source_files"][key])


if __name__ == "__main__":
    unittest.main()
