from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

try:
    from .barge_hydrodynamic_convergence import (
        DIAGONAL_LABELS,
        MESH_LEVELS,
        frequency_grid,
        parse_control_input,
        parse_hydrostatic_input,
        platform_properties,
        radiation_analysis,
    )
    from .common import read_json, resolve_case
except ImportError:
    from barge_hydrodynamic_convergence import DIAGONAL_LABELS, MESH_LEVELS, frequency_grid, parse_control_input, parse_hydrostatic_input, platform_properties, radiation_analysis
    from common import read_json, resolve_case


ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = resolve_case("Barge_120x50")


class BargeHydrodynamicConvergenceTest(unittest.TestCase):
    def test_existing_hydrostatic_values_are_read_from_hams_input(self) -> None:
        config = read_json(CASE_DIR / "platform_config.json")
        hydro = parse_hydrostatic_input(CASE_DIR / "Input" / "Hydrostatic.in")
        control = parse_control_input(CASE_DIR / "Input" / "ControlFile.in")
        properties = platform_properties(CASE_DIR, config, hydro, control)

        self.assertEqual(hydro["mass_kg"], 43_050_000.0)
        self.assertEqual(hydro["center_of_gravity_m"], [0.0, 0.0, -2.0])
        self.assertAlmostEqual(hydro["inertia_about_cg_kg_m2"]["Ixx_kg_m2"], 9_327_500_000.0)
        self.assertAlmostEqual(hydro["inertia_about_cg_kg_m2"]["Iyy_kg_m2"], 52_018_800_000.0)
        self.assertAlmostEqual(hydro["inertia_about_cg_kg_m2"]["Izz_kg_m2"], 60_628_800_000.0)
        self.assertAlmostEqual(properties["K33_N_m"], 60_310_900.0)
        self.assertAlmostEqual(properties["K44_Nm_rad"], 11_931_500_000.0)
        self.assertAlmostEqual(properties["K55_Nm_rad"], 71_739_800_000.0)
        self.assertTrue(np.allclose(properties["C_ext_linear_damping_matrix"], np.zeros((6, 6))))
        self.assertEqual(control["reference_point_m"], [0.0, 0.0, 0.0])

    def test_mesh_levels_hit_requested_panel_orders(self) -> None:
        expected = {"coarse": (512, 240), "medium": (2048, 960), "fine": (8192, 3840)}
        for name, spec in MESH_LEVELS.items():
            nx, ny, nz = int(spec["nx"]), int(spec["ny"]), int(spec["nz"])
            hull = nx * ny + 2 * nx * nz + 2 * ny * nz
            waterplane = nx * ny
            self.assertEqual(hull, expected[name][0])
            self.assertEqual(waterplane, expected[name][1])

    def test_frequency_grid_has_local_refinement_and_a_inf_targets(self) -> None:
        frequencies = frequency_grid("local025_high025")
        local = [value for value in frequencies if value <= 2.0]
        self.assertEqual(local[0], 0.2)
        self.assertEqual(local[-1], 2.0)
        self.assertTrue(all(abs((right - left) - 0.025) < 1.0e-9 for left, right in zip(local, local[1:])))
        self.assertIn(3.0, frequencies)
        self.assertIn(4.0, frequencies)
        self.assertIn(5.0, frequencies)
        self.assertEqual(frequencies, sorted(set(frequencies)))
        self.assertEqual(frequency_grid("mesh_response_anchor"), [0.6, 0.8, 1.0])

    def test_radiation_analysis_reconstructs_a_finite_synthetic_band(self) -> None:
        frequencies = [0.2 + 0.1 * index for index in range(29)]
        rows = []
        for frequency in frequencies:
            added = np.diag([10.0, 12.0, 14.0, 16.0, 18.0, 20.0]).tolist()
            damping = np.diag([2.0, 2.0, 3.0, 4.0, 5.0, 6.0]).tolist()
            rows.append({"frequency_rad_s": frequency, "added_mass_kg": added, "radiation_damping_kg_s": damping})
        result = radiation_analysis({"frequencies_rad_s": frequencies, "rows": rows})
        self.assertTrue(result["finite_values"])
        self.assertEqual(result["negative_damping_frequency_count"], 0)
        self.assertIn("33", {key for key in DIAGONAL_LABELS.values()})
        self.assertTrue(result["irf_reconstruction"]["kernel_finite"])
        self.assertTrue(np.isfinite(result["A_inf_diagonal_kg"]["33"]))


if __name__ == "__main__":
    unittest.main()
