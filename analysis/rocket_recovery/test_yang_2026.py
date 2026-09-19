from __future__ import annotations

import math
import unittest

import numpy as np

from .yang_2026 import (
    air_spring_force,
    audit_sea_change_claims,
    audit_table_2,
    impact_normal_force,
    load_reference,
    oil_damping_force,
    physics_consistent_drop_height,
    printed_drop_height_equation_value,
    simulate_unit_white_noise_deck,
)


class YangReferenceAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reference = load_reference()

    def test_drop_height_equation_is_audited_without_silent_correction(self) -> None:
        printed = printed_drop_height_equation_value(2.0)
        physical = physics_consistent_drop_height(2.0)
        self.assertAlmostEqual(physical, 2.0 * printed)
        self.assertAlmostEqual(physical, 2.0**2 / (2.0 * 9.80665))

    def test_table_2_audit_detects_publication_inconsistencies(self) -> None:
        audit = audit_table_2(self.reference)
        self.assertEqual(audit["row_count"], 9)
        self.assertFalse(audit["all_strict_rows_consistent"])
        inconsistent = [row for row in audit["rows"] if not row["internally_consistent"]]
        self.assertGreaterEqual(len(inconsistent), 4)

    def test_sea_case_percentages_are_recomputed_from_printed_scalars(self) -> None:
        audit = audit_sea_change_claims(self.reference)
        values = audit["recomputed_increase_percent"]
        self.assertTrue(math.isclose(values["maximum_buffer_stroke"], 12.757201646090544))
        self.assertGreater(values["peak_vertical_acceleration"], 16.0)

    def test_deck_filter_is_deterministic_for_a_fixed_seed(self) -> None:
        first = simulate_unit_white_noise_deck(self.reference, duration_s=2.0, dt_s=0.01, seed=42)
        second = simulate_unit_white_noise_deck(self.reference, duration_s=2.0, dt_s=0.01, seed=42)
        np.testing.assert_allclose(first["heave_time_series"], second["heave_time_series"])
        np.testing.assert_allclose(first["pitch_time_series"], second["pitch_time_series"])
        self.assertTrue(np.all(np.isfinite(first["heave_time_series"])))


class YangPublishedEquationTest(unittest.TestCase):
    def test_oil_damping_force_opposes_rebound_with_paper_sign_convention(self) -> None:
        common = dict(
            oil_density_kg_m3=850.0,
            compressed_oil_area_m2=0.01,
            compression_orifice_area_m2=1.0e-4,
            rebound_orifice_area_m2=8.0e-5,
            discharge_coefficient=0.7,
        )
        self.assertGreater(oil_damping_force(0.2, **common), 0.0)
        self.assertLess(oil_damping_force(-0.2, **common), 0.0)

    def test_air_spring_force_increases_with_compression(self) -> None:
        common = dict(
            initial_air_height_m=0.5,
            initial_pressure_pa=2.0e6,
            atmospheric_pressure_pa=101325.0,
            compressed_air_area_m2=0.01,
            polytropic_exponent=1.4,
        )
        self.assertGreater(air_spring_force(0.1, **common), air_spring_force(0.0, **common))

    def test_contact_force_is_unilateral(self) -> None:
        common = dict(
            stiffness_n_m_power=1.0e7,
            exponent=1.5,
            maximum_penetration_m=0.01,
            maximum_damping_ns_m=1.0e5,
        )
        self.assertEqual(impact_normal_force(-0.001, 1.0, **common), 0.0)
        self.assertGreater(impact_normal_force(0.001, 1.0, **common), 0.0)


if __name__ == "__main__":
    unittest.main()
