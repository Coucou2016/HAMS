from __future__ import annotations

import math
import unittest

import numpy as np

from .yang_2026_landing_identification import (
    IdentifiedParameters,
    leg_forces,
    leg_projected_coordinates,
    observed_stroke_from_vertical_compression,
    simulate_condition,
)


class YangReducedLandingModelTest(unittest.TestCase):
    @staticmethod
    def parameters() -> IdentifiedParameters:
        return IdentifiedParameters(
            force_observation_ratio=0.5,
            stroke_observation_ratio=0.8,
            vertical_stiffness_n_m=1.5e5,
            quadratic_vertical_stiffness_n_m2=0.0,
            compression_vertical_damping_ns_m=2.0e4,
            rebound_vertical_damping_ns_m=4.0e4,
        )

    def test_landing_sequences_follow_published_geometric_forms(self) -> None:
        radius = 3.0
        one_two_one = leg_projected_coordinates(radius, 0.0)
        two_two = leg_projected_coordinates(radius, 45.0)
        self.assertEqual(int(np.sum(np.isclose(one_two_one, np.max(one_two_one)))), 1)
        self.assertEqual(int(np.sum(np.isclose(two_two, np.max(two_two)))), 2)

    def test_zero_penetration_has_zero_force(self) -> None:
        force, vertical, stroke = leg_forces(np.zeros(4), np.ones(4), self.parameters())
        np.testing.assert_allclose(force, 0.0)
        np.testing.assert_allclose(vertical, 0.0)
        np.testing.assert_allclose(stroke, 0.0)

    def test_observed_stroke_uses_documented_constant_mapping(self) -> None:
        parameters = self.parameters()
        delta = np.asarray([0.01, 0.02, 0.03])
        stroke = observed_stroke_from_vertical_compression(delta, parameters)
        np.testing.assert_allclose(stroke * parameters.stroke_observation_ratio, delta)

    def test_observed_main_strut_force_maps_from_vertical_force(self) -> None:
        parameters = self.parameters()
        strut_force, vertical_force, _ = leg_forces(np.asarray([0.02]), np.asarray([0.0]), parameters)
        np.testing.assert_allclose(strut_force * parameters.force_observation_ratio, vertical_force)

    def test_nominal_simulation_is_finite_and_contacts_all_legs(self) -> None:
        result = simulate_condition("Y0_simultaneous", self.parameters(), dt_s=0.002, duration_s=0.8)
        self.assertTrue(np.all(np.isfinite(result["states"])))
        self.assertEqual(len(result["touchdown_sequence"]), 4)
        times = [row["first_contact_time_s"] for row in result["touchdown_sequence"]]
        self.assertTrue(all(math.isclose(value, times[0], abs_tol=0.002) for value in times))


if __name__ == "__main__":
    unittest.main()
