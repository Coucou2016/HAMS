from __future__ import annotations

import unittest

import numpy as np

from .chrono_leg_model import DeckMotion


class DeckMotionInterpolationTest(unittest.TestCase):
    def make_motion(self) -> DeckMotion:
        time = np.array([0.0, 1.0])
        position = time**3
        velocity = 3.0 * time**2
        zeros = np.zeros_like(time)
        return DeckMotion(
            time_s=time,
            heave_m=position,
            roll_rad=zeros,
            pitch_rad=zeros,
            heave_m_s=velocity,
            roll_rad_s=zeros,
            pitch_rad_s=zeros,
        )

    def test_cubic_position_and_velocity_are_reproduced(self) -> None:
        sample = self.make_motion().sample(0.4)
        self.assertAlmostEqual(sample["heave_m"], 0.4**3, places=12)
        self.assertAlmostEqual(sample["heave_m_s"], 3.0 * 0.4**2, places=12)

    def test_endpoint_state_is_preserved(self) -> None:
        motion = self.make_motion()
        self.assertEqual(motion.sample(-1.0)["heave_m"], 0.0)
        self.assertEqual(motion.sample(2.0)["heave_m"], 1.0)
        self.assertEqual(motion.sample(2.0)["heave_m_s"], 3.0)


if __name__ == "__main__":
    unittest.main()
