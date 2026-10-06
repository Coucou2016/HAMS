from __future__ import annotations

import unittest

from .chrono_leg_model import explicit_smc_contact_audit, multibody_mass_audit, tripod_leg_model_config


class ChronoExplicitContactAuditTest(unittest.TestCase):
    def test_literature_damping_is_converted_to_chrono_rate(self) -> None:
        config = tripod_leg_model_config()
        audit = explicit_smc_contact_audit(config)
        self.assertEqual(audit["coefficient_mode"], "explicit_stiffness_damping")
        self.assertAlmostEqual(audit["normal_stiffness_kn_n_m"], 100.0e6)
        self.assertAlmostEqual(audit["configured_normal_damping_cn_ns_m"], 10.0e3)
        self.assertAlmostEqual(audit["material_Gn_s_inv"], 125.003, places=3)
        self.assertAlmostEqual(
            audit["reference_effective_contact_mass_kg"] * audit["material_Gn_s_inv"],
            audit["configured_normal_damping_cn_ns_m"],
            places=6,
        )

    def test_explicit_child_bodies_do_not_increase_published_total_mass(self) -> None:
        audit = multibody_mass_audit(tripod_leg_model_config())
        self.assertAlmostEqual(audit["mass_residual_kg"], 0.0)
        self.assertAlmostEqual(audit["explicit_footpad_mass_kg"], 320.0)
        self.assertAlmostEqual(
            audit["rocket_body_mass_kg"] + audit["explicit_footpad_mass_kg"],
            audit["published_total_landing_mass_kg"],
        )


if __name__ == "__main__":
    unittest.main()
