from __future__ import annotations

import math
import unittest

import numpy as np

from .common import trapezoid_integral
from .deck_point_rao import transform_motion
from .landing_leg_contact import deck_footprint_envelope, kinetic_energy_kj, thies_footprint_radius_m
from .sea_state_response import jonswap_spectrum, spectrum_band_audit
from .reviewer_matrix_audit import matrix_checks
from .chrono_two_way_recovery import (
    DOF_NAMES_6DOF,
    compare_time_step_series_6dof,
    generalized_leg_force_from_chrono_6dof,
    inverse_square_matrix,
    make_time_grid,
    rocket_energy_diagnostic,
    solve_cummins_leg_correction,
)


class DeckPointTransformTest(unittest.TestCase):
    def test_pure_heave_same_at_all_points(self) -> None:
        dofs = {str(i): 0j for i in range(1, 7)}
        dofs["3"] = 1.25 + 0.5j
        for point in ([0.0, 0.0, 3.0], [9.0, 9.0, 3.0], [-9.0, -9.0, 3.0]):
            result = transform_motion(dofs, list(point), 1.0)
            self.assertEqual(result["displacement_m"]["z"], dofs["3"])

    def test_pure_roll_vertical_motion_depends_on_y(self) -> None:
        dofs = {str(i): 0j for i in range(1, 7)}
        dofs["4"] = 0.1 + 0j
        result = transform_motion(dofs, [0.0, 9.0, 3.0], 2.0)
        self.assertAlmostEqual(result["displacement_m"]["z"].real, 0.9)
        self.assertAlmostEqual(result["velocity_m_s"]["z"].imag, 1.8)

    def test_pure_pitch_vertical_motion_depends_on_negative_x(self) -> None:
        dofs = {str(i): 0j for i in range(1, 7)}
        dofs["5"] = 0.1 + 0j
        result = transform_motion(dofs, [9.0, 0.0, 3.0], 2.0)
        self.assertAlmostEqual(result["displacement_m"]["z"].real, -0.9)
        self.assertAlmostEqual(result["velocity_m_s"]["z"].imag, -1.8)


class SpectrumTest(unittest.TestCase):
    def test_raw_reciprocity_is_measured_before_symmetrization(self) -> None:
        matrix = np.eye(6)
        matrix[0, 1] = 0.5
        self.assertGreater(matrix_checks(matrix, 120)["raw_reciprocity_relative_frobenius"], 0)
        matrix[1, 0] = 0.5
        self.assertEqual(matrix_checks(matrix, 120)["raw_reciprocity_relative_frobenius"], 0)
        matrix[2, 2] = -1
        self.assertLess(matrix_checks(matrix, 120)["relative_minimum_eigenvalue"], 0)

    def test_full_normalization_does_not_redistribute_missing_tail(self) -> None:
        omega = np.linspace(0.2, 2.0, 1801).tolist()
        audit = spectrum_band_audit(omega, 2.0, 6.0)
        self.assertAlmostEqual(audit["captured_variance_fraction"], 0.94119, places=4)
        full = jonswap_spectrum(omega, 2.0, 6.0, normalization="full")
        band = jonswap_spectrum(omega, 2.0, 6.0, normalization="band")
        np.testing.assert_allclose(np.asarray(band) * audit["captured_variance_fraction"], full)
        wider = spectrum_band_audit(np.linspace(0.2, 5.0, 4801).tolist(), 2.0, 6.0)
        self.assertGreater(wider["captured_variance_fraction"], 0.998)

    def test_kinetic_decay_is_not_energy_balance_validation(self) -> None:
        config = {"rocket": {"landing_mass_kg": 10, "inertia_kg_m2": {"roll_x": 1, "pitch_y": 1, "yaw_z": 1}}}
        sim = {"rocket": {"vertical_velocity_m_s": [2, 0], "roll_rate_rad_s": [0, 0], "pitch_rate_rad_s": [0, 0], "yaw_rate_rad_s": [0, 0]}}
        result = rocket_energy_diagnostic(config, sim)
        self.assertTrue(result["kinetic_energy_decreased"])
        self.assertIsNone(result["pass"])
        self.assertEqual(result["status"], "incomplete_energy_budget")

    def test_jonswap_is_scaled_to_hs(self) -> None:
        frequencies = [0.2 + 0.02 * i for i in range(120)]
        spectrum = jonswap_spectrum(frequencies, hs_m=2.0, tp_s=8.0)
        m0 = trapezoid_integral(frequencies, spectrum)
        self.assertTrue(math.isclose(m0, 2.0**2 / 16.0, rel_tol=1.0e-9))

    def test_time_grid_hits_requested_end_point_exactly(self) -> None:
        time_s = make_time_grid(506.0, 526.0, 0.005)
        self.assertEqual(len(time_s), 4001)
        self.assertEqual(float(time_s[0]), 506.0)
        self.assertEqual(float(time_s[-1]), 526.0)
        np.testing.assert_allclose(np.diff(time_s), 0.005, rtol=0.0, atol=1.0e-12)

    def test_time_step_comparison_uses_common_physical_grid(self) -> None:
        coarse_time = np.array([0.0, 0.5, 1.0], dtype=float)
        fine_time = np.array([0.0, 0.25, 0.5, 0.75, 1.0], dtype=float)

        def series(time_s: np.ndarray) -> dict:
            q = np.column_stack([time_s * (column + 1.0) for column in range(6)])
            qd = np.column_stack([np.full(len(time_s), column + 1.0) for column in range(6)])
            return {
                "time_s": time_s.tolist(),
                "responses": {
                    "surge_m": q[:, 0].tolist(),
                    "sway_m": q[:, 1].tolist(),
                    "heave_m": q[:, 2].tolist(),
                    "roll_rad": q[:, 3].tolist(),
                    "pitch_rad": q[:, 4].tolist(),
                    "yaw_rad": q[:, 5].tolist(),
                },
                "velocities": {
                    "surge_m_s": qd[:, 0].tolist(),
                    "sway_m_s": qd[:, 1].tolist(),
                    "heave_m_s": qd[:, 2].tolist(),
                    "roll_rad_s": qd[:, 3].tolist(),
                    "pitch_rad_s": qd[:, 4].tolist(),
                    "yaw_rad_s": qd[:, 5].tolist(),
                },
            }

        result = compare_time_step_series_6dof(series(coarse_time), series(fine_time))
        self.assertTrue(result["pass"])
        self.assertEqual(result["sample_count"], len(fine_time))
        self.assertEqual(result["time_start_s"], 0.0)
        self.assertEqual(result["time_end_s"], 1.0)


class LandingLegEnvelopeTest(unittest.TestCase):
    def test_thies_nominal_energy_matches_table(self) -> None:
        energy = kinetic_energy_kj(61_288.0, 5.0)
        self.assertTrue(math.isclose(energy, 766.1, rel_tol=5.0e-4))

    def test_thies_footprint_radius_uses_paper_geometry(self) -> None:
        radius = thies_footprint_radius_m()
        expected = 8.1 * math.cos(math.radians(33.0))
        self.assertAlmostEqual(radius, expected)

    def test_deck_envelope_for_pure_roll(self) -> None:
        radius = 6.0
        env = deck_footprint_envelope(
            heave_m=[0.0],
            roll_rad=[0.1],
            pitch_rad=[0.0],
            heave_m_s=[0.2],
            roll_rad_s=[0.01],
            pitch_rad_s=[0.0],
            radius_m=radius,
        )
        self.assertAlmostEqual(float(env["foot_vertical_spread_m"][0]), 2.0 * radius * 0.1)
        self.assertAlmostEqual(float(env["deck_vz_min_m_s"][0]), 0.2 - radius * 0.01)
        self.assertAlmostEqual(float(env["deck_vz_max_m_s"][0]), 0.2 + radius * 0.01)


class ChronoSixDofForceMappingTest(unittest.TestCase):
    @staticmethod
    def _single_leg_sim(force_xyz: tuple[float, float, float], position_xyz: tuple[float, float, float]) -> dict:
        time_s = [0.0, 1.0]
        force_x, force_y, force_z = force_xyz
        position_x, position_y, position_z = position_xyz
        return {
            "time_s": time_s,
            "forces": {
                "leg_contact_force_xyz_n": {
                    "leg_1": {
                        "x": [force_x, force_x],
                        "y": [force_y, force_y],
                        "z": [force_z, force_z],
                    }
                }
            },
            "feet": {
                "position_m": {
                    "leg_1": {
                        "x_m": [position_x, position_x],
                        "y_m": [position_y, position_y],
                        "z_m": [position_z, position_z],
                    }
                }
            },
        }

    def test_dof_order_is_platform_six_dof_order(self) -> None:
        self.assertEqual(
            DOF_NAMES_6DOF,
            ["surge_m", "sway_m", "heave_m", "roll_rad", "pitch_rad", "yaw_rad"],
        )

    def test_vertical_contact_maps_to_equal_opposite_force_and_r_cross_f_moment(self) -> None:
        sim = self._single_leg_sim((0.0, 0.0, 1_000.0), (2.0, 3.0, 4.0))

        result = generalized_leg_force_from_chrono_6dof(
            sim,
            np.array([0.0, 1.0]),
        )
        values = np.asarray(result["values_6dof"], dtype=float)

        # Chrono reports contact force on the rocket. The platform receives -F.
        # For r=(2,3,4) and F_platform=(0,0,-1000), r x F=(-3000,2000,0).
        expected = np.array([0.0, 0.0, -1_000.0, -3_000.0, 2_000.0, 0.0])
        np.testing.assert_allclose(values[0], expected)
        np.testing.assert_allclose(values[1], expected)

    def test_horizontal_contact_at_nonzero_xyz_maps_all_platform_moments(self) -> None:
        sim = self._single_leg_sim((100.0, 200.0, 300.0), (2.0, 3.0, 4.0))

        result = generalized_leg_force_from_chrono_6dof(
            sim,
            np.array([0.0, 1.0]),
            footpad_radius_m=0.5,
        )
        values = np.asarray(result["values_6dof"], dtype=float)

        # The application point is the footpad centre minus its radius in z:
        # r=(2,3,3.5), F_platform=(-100,-200,-300).
        # Therefore r x F=(-200,250,-100) N m.
        expected = np.array([-100.0, -200.0, -300.0, -200.0, 250.0, -100.0])
        np.testing.assert_allclose(values[0], expected)
        np.testing.assert_allclose(values[1], expected)

    def test_footpad_contact_point_follows_rotated_deck_normal(self) -> None:
        sim = self._single_leg_sim((0.0, 0.0, 1_000.0), (2.0, 3.0, 4.0))
        roll = 0.1
        sim["deck"] = {
            "roll_rad": [roll, roll],
            "pitch_rad": [0.0, 0.0],
            "yaw_rad": [0.0, 0.0],
        }

        result = generalized_leg_force_from_chrono_6dof(
            sim,
            np.array([0.0, 1.0]),
            footpad_radius_m=0.5,
        )
        values = np.asarray(result["values_6dof"], dtype=float)

        contact_y = 3.0 + 0.5 * math.sin(roll)
        expected_roll_moment = contact_y * -1_000.0
        self.assertAlmostEqual(values[0, 3], expected_roll_moment)
        self.assertAlmostEqual(values[1, 3], expected_roll_moment)


class CumminsSixDofCorrectionTest(unittest.TestCase):
    def test_six_by_six_zero_external_force_returns_zero_correction(self) -> None:
        time_s = np.array([0.0, 0.1, 0.2, 0.3])
        external_force = np.zeros((len(time_s), 6), dtype=float)
        matrices = {
            "omega_rad_s": np.array([0.5, 1.0], dtype=float),
            "radiation_damping": np.zeros((2, 6, 6), dtype=float),
            "radiation_weights": np.ones(2, dtype=float),
            "mass": np.diag([10.0, 11.0, 12.0, 13.0, 14.0, 15.0]),
            "linear_damping": np.zeros((6, 6), dtype=float),
            "restoring": np.zeros((6, 6), dtype=float),
        }

        result = solve_cummins_leg_correction(matrices, time_s, external_force, 0.1)

        self.assertEqual(np.asarray(result["q"]).shape, (len(time_s), 6))
        self.assertEqual(np.asarray(result["qd"]).shape, (len(time_s), 6))
        self.assertEqual(np.asarray(result["memory_force"]).shape, (len(time_s), 6))
        np.testing.assert_allclose(result["q"], 0.0)
        np.testing.assert_allclose(result["qd"], 0.0)
        np.testing.assert_allclose(result["memory_force"], 0.0)

    def test_six_by_six_nonzero_force_runs_matrix_inverse_path(self) -> None:
        time_s = np.array([0.0, 0.1, 0.2], dtype=float)
        external_force = np.zeros((len(time_s), 6), dtype=float)
        external_force[:, 0] = 10.0
        matrices = {
            "omega_rad_s": np.array([0.5], dtype=float),
            "radiation_damping": np.zeros((1, 6, 6), dtype=float),
            "radiation_weights": np.ones(1, dtype=float),
            "mass": np.diag([10.0, 11.0, 12.0, 13.0, 14.0, 15.0]),
            "linear_damping": np.zeros((6, 6), dtype=float),
            "restoring": np.zeros((6, 6), dtype=float),
        }

        inverse = inverse_square_matrix(matrices["mass"])
        np.testing.assert_allclose(inverse, np.diag([0.1, 1.0 / 11.0, 1.0 / 12.0, 1.0 / 13.0, 1.0 / 14.0, 1.0 / 15.0]))
        result = solve_cummins_leg_correction(matrices, time_s, external_force, 0.1)

        self.assertTrue(np.all(np.isfinite(result["q"])))
        self.assertGreater(float(result["q"][-1, 0]), 0.0)
        np.testing.assert_allclose(np.asarray(result["q"])[:, 1:], 0.0)


if __name__ == "__main__":
    unittest.main()
