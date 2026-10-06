# 原始代码定位证据

## R01_inertia_frame

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第109–127行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
109:             "source": rocket["source"],
110:             "landing_mass_kg": rocket["landing_mass_kg"],
111:             "mass_allocation": "published_total_less_explicit_multibody_children",
112:             "height_m": rocket["height_m"],
113:             "engine_length_m": rocket["engine_length_m"],
114:             "base_diameter_m": rocket["base_diameter_m"],
115:             "cog_from_base_m": rocket["cog_from_launcher_base_m"],
116:             "inertia_kg_m2": {
117:                 "roll_x": rocket["inertia_kg_m2"]["roll_iyy"],
118:                 "pitch_y": rocket["inertia_kg_m2"]["pitch_ixx"],
119:                 "yaw_z": rocket["inertia_kg_m2"]["yaw_izz"],
120:             },
121:             "touchdown_vertical_velocity_m_s": req["touchdown_vertical_velocity_nominal_m_s"],
122:             "initial_lateral_velocity_m_s": req["touchdown_lateral_velocity_nominal_m_s"],
123:             "nozzle_clearance_required_m": rocket["allowed_nozzle_clearance_m"],
124:             "reported_nozzle_clearance_m": result["nozzle_clearance_m"],
125:             "stage3_proxy_nozzle_reference_height_from_model_base_m": result["nozzle_clearance_m"],
126:             "stage3_proxy_nozzle_reference_note": (
127:                 "Thies reports nozzle clearance as distance from nozzle end to landing pad. "
```

## R01_body_inertia_application

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第988–1016行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
988: def make_rocket_body(chrono: Any, config: dict[str, Any], material: Any) -> Any:
989:     rocket = config["rocket"]
990:     # Collision on the rocket body is disabled; footpads own the ground contact.
991:     body = chrono.ChBody()
992:     published_total_mass = float(rocket["landing_mass_kg"])
993:     explicit_child_mass = float(config["legs"]["count"]) * float(config["legs"]["footpad_mass_kg"])
994:     rigid_links = config.get("legs", {}).get("stage3_tripod_proxy", {}).get("rigid_body_links", {})
995:     if rigid_links:
996:         explicit_child_mass += float(config["legs"]["count"]) * float(rigid_links.get("rod_total_mass_per_leg_kg", 0.0))
997:     if rocket.get("mass_allocation") != "published_total_less_explicit_multibody_children":
998:         raise ChronoUnavailableError("Rocket mass allocation must prevent explicit child bodies from double-counting published landing mass.")
999:     rocket_body_mass = published_total_mass - explicit_child_mass
1000:     if rocket_body_mass <= 0.0:
1001:         raise ChronoUnavailableError("Explicit multibody child mass exceeds the published landing mass.")
1002:     body.SetMass(rocket_body_mass)
1003:     body.SetInertiaXX(
1004:         chrono_vec(
1005:             chrono,
1006:             float(rocket["inertia_kg_m2"]["roll_x"]),
1007:             float(rocket["inertia_kg_m2"]["pitch_y"]),
1008:             float(rocket["inertia_kg_m2"]["yaw_z"]),
1009:         )
1010:     )
1011:     enable_collision(body, False)
1012:     return body
1013: 
1014: 
1015: def make_tsda(chrono: Any, rocket_body: Any, foot_body: Any, rocket_anchor: Any, foot_anchor: Any, config: dict[str, Any]) -> Any:
1016:     if not hasattr(chrono, "ChLinkTSDA"):
```

## R02_collision_geometry

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第1495–1535行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
1495:         self.chrono = import_pychrono()
1496: 
1497:     def run(self) -> dict[str, Any]:  # pragma: no cover - exercised only when PyChrono is installed
1498:         chrono = self.chrono
1499:         config = self.config
1500:         system = make_system(chrono, config)
1501:         material = make_contact_material(chrono, config)
1502: 
1503:         deck_thickness = float(config["solver"]["deck_thickness_m"])
1504:         deck = make_box_body(chrono, (180.0, 54.0, deck_thickness), 1000.0, material, True)
1505:         set_body_fixed(deck, True)
1506:         add_to_system(system, deck)
1507: 
1508:         rocket = make_rocket_body(chrono, config, material)
1509:         leg_rows = leg_positions_from_config(config)
1510:         touchdown = 510.0
1511:         cg = float(config["rocket"]["cog_from_base_m"])
1512:         foot_radius = float(config["legs"]["footpad_radius_m"])
1513:         touchdown_v = float(config["rocket"]["touchdown_vertical_velocity_m_s"])
1514:         target_x, target_y = self.deck_motion.deck_xy(touchdown, self.deck_motion.offset_x_m, self.deck_motion.offset_y_m)
1515:         deck_touch_z = self.deck_motion.deck_z(touchdown, target_x, target_y)
1516:         start = float(config["solver"]["start_s"])
1517:         initial_z = deck_touch_z + cg + touchdown_v * (touchdown - start)
1518:         rocket.SetPos(chrono_vec(chrono, target_x, target_y, initial_z))
1519:         set_body_velocity(rocket, chrono, 0.0, 0.0, -touchdown_v)
1520:         add_to_system(system, rocket)
1521:         rocket_origin = (target_x, target_y, initial_z)
1522:         rocket_base_z = initial_z - cg
1523: 
1524:         feet: dict[str, Any] = {}
1525:         springs: dict[str, Any] = {}
1526:         spring_functors: list[Any] = []
1527:         braces: dict[str, dict[str, Any]] = {}
1528:         anchors: dict[str, dict[str, tuple[float, float, float]]] = {}
1529:         foot_density = max(1.0, float(config["legs"]["footpad_mass_kg"]) / (4.0 / 3.0 * math.pi * foot_radius**3))
1530:         proxy = config["legs"]["stage3_tripod_proxy"]
1531:         for leg in leg_rows:
1532:             leg_id = leg["id"]
1533:             pts = tripod_anchor_points(config, leg, target_x, target_y, rocket_base_z)
1534:             anchors[leg_id] = pts
1535:             foot = make_sphere_body(chrono, foot_radius, foot_density, material, True)
```

## R02_collision_pose

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第1717–1736行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
1717:             raise ValueError("Chrono simulation interval must be an integer multiple of time_step_s.")
1718: 
1719:         for step_index in range(step_count + 1):
1720:             t = end if step_index == step_count else start + step_index * dt
1721:             deck_state = self.deck_motion.sample(t)
1722:             deck.SetPos(chrono_vec(chrono, deck_state["surge_m"], deck_state["sway_m"], deck_state["heave_m"] - 0.5 * deck_thickness))
1723:             deck.SetRot(
1724:                 chrono_quat_from_roll_pitch_yaw(
1725:                     chrono,
1726:                     deck_state["roll_rad"],
1727:                     deck_state["pitch_rad"],
1728:                     deck_state["yaw_rad"],
1729:                 )
1730:             )
1731:             set_body_velocity(deck, chrono, deck_state["surge_m_s"], deck_state["sway_m_s"], deck_state["heave_m_s"])
1732:             set_body_angular_velocity(deck, chrono, deck_state["roll_rad_s"], deck_state["pitch_rad_s"], deck_state["yaw_rad_s"])
1733:             if not first_contact_seen:
1734:                 first_contact_seen = any(body.GetContactForce().z > contact_force_threshold for body in feet.values())
1735:             if first_contact_seen:
1736:                 set_system_gravity(system, chrono, -gravity)
```

## R02_legacy_plane

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第626–650行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
626:             "pitch_rad_s": pitch_rate,
627:             "yaw_rad_s": yaw_rate,
628:         }
629: 
630:     def deck_xy(self, t: float, x_local_m: float, y_local_m: float) -> tuple[float, float]:
631:         row = self.sample(t)
632:         yaw = row["yaw_rad"]
633:         c = math.cos(yaw)
634:         s = math.sin(yaw)
635:         return (
636:             row["surge_m"] + c * x_local_m - s * y_local_m,
637:             row["sway_m"] + s * x_local_m + c * y_local_m,
638:         )
639: 
640:     def deck_z(self, t: float, x_m: float, y_m: float) -> float:
641:         row = self.sample(t)
642:         dx = x_m - row["surge_m"]
643:         dy = y_m - row["sway_m"]
644:         yaw = row["yaw_rad"]
645:         c = math.cos(yaw)
646:         s = math.sin(yaw)
647:         local_x = c * dx + s * dy
648:         local_y = -s * dx + c * dy
649:         return row["heave_m"] + row["roll_rad"] * local_y - row["pitch_rad"] * local_x
650: 
```

## R03_actual_resampler

`analysis/rocket_recovery/chrono_two_way_recovery.py`，原文件第784–816行。

SHA-256 `b30f3b931929e6b025184eb4e3d6b84733cf9b1d99cfc1fa32689ab48a8261fa`

```text
784:         "max_surge_action_reaction_residual_n": float(force_residual[0]),
785:         "max_sway_action_reaction_residual_n": float(force_residual[1]),
786:         "max_vertical_action_reaction_residual_n": float(force_residual[2]),
787:         "max_roll_moment_residual_nm": float(moment_residual[0]),
788:         "max_pitch_moment_residual_nm": float(moment_residual[1]),
789:         "max_yaw_moment_residual_nm": float(moment_residual[2]),
790:         "max_omitted_horizontal_contact_force_n": 0.0,
791:         "max_horizontal_contact_force_fed_back_n": float(np.max(horizontal_contact)) if sample_count else 0.0,
792:         "horizontal_force_feedback_included": True,
793:         "lock_reaction_included": lock_available,
794:         "max_lock_vertical_platform_force_n": float(np.max(np.abs(lock_samples[:, 2]))) if sample_count else 0.0,
795:         "max_lock_roll_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 3]))) if sample_count else 0.0,
796:         "max_lock_pitch_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 4]))) if sample_count else 0.0,
797:         "max_lock_yaw_platform_moment_nm": float(np.max(np.abs(lock_samples[:, 5]))) if sample_count else 0.0,
798:         "contact_application_point": "Chrono spherical footpad center minus radius along the prescribed deck normal.",
799:         "coordinate_frame": "Chrono world axes aligned with the HAMS reference axes; moments are about XR=(0,0,0).",
800:         "sign_convention": "Chrono contact and lock reactions act on the rocket/footpads. Platform generalized load is the equal and opposite [Fx,Fy,Fz,Mx,My,Mz].",
801:     }
802:     target = np.column_stack(
803:         [np.interp(target_time_s, chrono_time, platform_samples[:, column]) for column in range(6)]
804:     )
805:     return {
806:         "time_s": target_time_s,
807:         "values_6dof": target,
808:         "samples_time_s": chrono_time,
809:         "samples_6dof": platform_samples,
810:         "force_audit": audit,
811:         "summary": {
812:             "max_surge_platform_force_mn": float(np.max(np.abs(platform_samples[:, 0])) / 1.0e6) if sample_count else 0.0,
813:             "max_sway_platform_force_mn": float(np.max(np.abs(platform_samples[:, 1])) / 1.0e6) if sample_count else 0.0,
814:             "max_downward_platform_force_mn": float(np.max(np.abs(np.minimum(platform_samples[:, 2], 0.0))) / 1.0e6) if sample_count else 0.0,
815:             "max_roll_moment_mnm": float(np.max(np.abs(platform_samples[:, 3])) / 1.0e6) if sample_count else 0.0,
816:             "max_pitch_moment_mnm": float(np.max(np.abs(platform_samples[:, 4])) / 1.0e6) if sample_count else 0.0,
```

## R03_actual_caller

`analysis/rocket_recovery/chrono_same_platform_multibody.py`，原文件第193–214行。

SHA-256 `dfa6d89a538e58669e207ed5c53fbe4a457f0cdea8634850e96a7b99a59da8f1`

```text
193:     config = landing_config(contact_dt_s, end_s=end_s, contact_stiffness_n_m=contact_stiffness_n_m)
194:     offset = {"x": 0.0, "y": 15.0}
195:     rows: list[dict[str, Any]] = []
196:     final_sim: dict[str, Any] | None = None
197:     final_force6: dict[str, Any] | None = None
198:     for pass_index in range(1, pass_count + 1):
199:         motion = deck_motion_from_arrays(platform_time, current["q_active"], current["qd_active"], offset)
200:         sim = ChronoTripodLegModel(config, motion).run()
201:         force6 = generalized_leg_force_from_chrono_6dof(
202:             sim,
203:             platform_time,
204:             footpad_radius_m=float(config["legs"]["footpad_radius_m"]),
205:         )
206:         feedback = np.asarray(force6["values_6dof"], dtype=float)[:, ACTIVE_DOF_INDICES]
207:         updated = solve_platform(operator, study, wang_config, wave, platform_time, feedback)
208:         rows.append(
209:             {
210:                 "pass": pass_index,
211:                 "trajectory_change": trajectory_difference(current, updated),
212:                 "contact_summary": sim["summary"],
213:                 "wrench_summary": force6["summary"],
214:                 "wrench_action_reaction": force6["force_audit"],
```

## R04_compact_retention

`analysis/rocket_recovery/chrono_same_platform_multibody.py`，原文件第256–273行。

SHA-256 `dfa6d89a538e58669e207ed5c53fbe4a457f0cdea8634850e96a7b99a59da8f1`

```text
256:         compact = compact_simulation(final_sim, max_points=4000)
257:         compact["contact_model"] = final_sim.get("contact_model")
258:         compact["mass_model"] = final_sim.get("mass_model")
259:         result["response"] = {
260:             "platform_time_s": platform_time.tolist(),
261:             "baseline_q_active": np.asarray(baseline["q_active"]).tolist(),
262:             "final_q_active": np.asarray(current["q_active"]).tolist(),
263:             "final_qd_active": np.asarray(current["qd_active"]).tolist(),
264:             "multibody": compact,
265:             "platform_wrench_6dof": np.asarray(final_force6["values_6dof"]).tolist(),
266:         }
267:     return result
268: 
269: 
270: def convergence_summary(runs: dict[str, dict[str, Any]]) -> dict[str, Any]:
271:     metrics = {
272:         "max_leg_contact_force_kn": lambda row: float(row["final_contact_summary"]["max_leg_contact_force_kn"]),
273:         "max_leg_stroke_m": lambda row: float(row["final_contact_summary"]["max_leg_stroke_m"]),
```

## R05_force_definition

`analysis/rocket_recovery/chrono_leg_model.py`，原文件第1808–1829行。

SHA-256 `f40a2bfb889a2e24c70f6b405ecd5d218d7d2cb74a7bc11f383259faa7fb824f`

```text
1808:                     leg_id = leg["id"]
1809:                     fp = body_pos(feet[leg_id])
1810:                     vertices.append((fp[0], fp[1]))
1811:                     cf = feet[leg_id].GetContactForce()
1812:                     local_deck_z = self.deck_motion.deck_z(t, fp[0], fp[1])
1813:                     penetration = max(0.0, local_deck_z - (fp[2] - foot_radius))
1814:                     stroke = max(0.0, float(config["legs"]["damper_rest_length_m"]) - float(springs[leg_id].GetLength()))
1815:                     foot_position[leg_id]["x_m"].append(fp[0])
1816:                     foot_position[leg_id]["y_m"].append(fp[1])
1817:                     foot_position[leg_id]["z_m"].append(fp[2])
1818:                     leg_stroke[leg_id].append(stroke)
1819:                     leg_contact_penetration[leg_id].append(penetration)
1820:                     leg_contact[leg_id].append(1 if cf.z > contact_force_threshold or penetration > 1.0e-5 else 0)
1821:                     local_fp = point_in_body_local(rocket, fp)
1822:                     leg_slip[leg_id].append(math.hypot(local_fp[0] - leg["x_m"], local_fp[1] - leg["y_m"]))
1823:                     leg_force[leg_id].append(float(abs(springs[leg_id].GetForce())))
1824:                     leg_contact_force[leg_id].append(float(max(0.0, cf.z)))
1825:                     leg_contact_force_xyz[leg_id]["x"].append(float(cf.x))
1826:                     leg_contact_force_xyz[leg_id]["y"].append(float(cf.y))
1827:                     leg_contact_force_xyz[leg_id]["z"].append(float(cf.z))
1828:                     for brace_id, target in [
1829:                         ("long_brace", float(proxy["target_lengths_m"]["long_brace"])),
```

## R06_work_reference

`analysis/rocket_recovery/chrono_same_platform_multibody.py`，原文件第65–103行。

SHA-256 `dfa6d89a538e58669e207ed5c53fbe4a457f0cdea8634850e96a7b99a59da8f1`

```text
65: def coupling_work_audit(sim: dict[str, Any], force6: dict[str, Any]) -> dict[str, Any]:
66:     time = np.asarray(sim["time_s"], dtype=float)
67:     platform_wrench = np.asarray(force6["samples_6dof"], dtype=float)
68:     rocket_wrench = -platform_wrench
69:     deck = sim["deck"]
70:     rocket = sim["rocket"]
71:     platform_velocity = np.column_stack(
72:         [
73:             np.asarray(deck["surge_m_s"], dtype=float),
74:             np.asarray(deck["sway_m_s"], dtype=float),
75:             np.asarray(deck["heave_m_s"], dtype=float),
76:             np.asarray(deck["roll_rad_s"], dtype=float),
77:             np.asarray(deck["pitch_rad_s"], dtype=float),
78:             np.asarray(deck["yaw_rad_s"], dtype=float),
79:         ]
80:     )
81:     rocket_velocity = np.column_stack(
82:         [
83:             np.gradient(np.asarray(rocket["cg_x_m"], dtype=float), time),
84:             np.gradient(np.asarray(rocket["cg_y_m"], dtype=float), time),
85:             np.asarray(rocket["vertical_velocity_m_s"], dtype=float),
86:             np.asarray(rocket["roll_rate_rad_s"], dtype=float),
87:             np.asarray(rocket["pitch_rate_rad_s"], dtype=float),
88:             np.asarray(rocket["yaw_rate_rad_s"], dtype=float),
89:         ]
90:     )
91:     platform_work = float(np.trapezoid(np.einsum("ni,ni->n", platform_wrench, platform_velocity), time))
92:     rocket_work = float(np.trapezoid(np.einsum("ni,ni->n", rocket_wrench, rocket_velocity), time))
93:     pair_work = platform_work + rocket_work
94:     return {
95:         "platform_contact_work_j": platform_work,
96:         "rocket_contact_work_j": rocket_work,
97:         "contact_pair_work_j": pair_work,
98:         "contact_pair_dissipation_proxy_j": max(0.0, -pair_work),
99:         "definition": "Generalized equal-and-opposite contact wrench dotted with recorded platform and rocket generalized velocities; unresolved contact elastic energy is not hidden.",
100:     }
101: 
102: 
103: def absorber_work_audit(sim: dict[str, Any]) -> dict[str, Any]:
```

## R07_study_counts

`analysis/rocket_recovery/chrono_same_platform_multibody.py`，原文件第370–405行。

SHA-256 `dfa6d89a538e58669e207ed5c53fbe4a457f0cdea8634850e96a7b99a59da8f1`

```text
370: 
371: def build_report(skip_convergence: bool = False) -> dict[str, Any]:
372:     iterative = run_passes(4, 0.0005, retain_response=True, end_s=526.0)
373:     algorithm_rows = {
374:         "prescribed_deck": iterative["passes"][0]["contact_summary"],
375:         "one_pass_platform_update": iterative["passes"][0],
376:         "two_pass_platform_update": iterative["passes"][1],
377:         "four_pass_platform_update": iterative["passes"][3],
378:     }
379:     convergence_runs: dict[str, dict[str, Any]] = {}
380:     regularization_runs: dict[str, dict[str, Any]] = {}
381:     if not skip_convergence:
382:         convergence_runs["dt"] = run_passes(2, 0.0005, retain_response=False, end_s=516.0)
383:         convergence_runs["dt_over_2"] = run_passes(2, 0.00025, retain_response=False, end_s=516.0)
384:         convergence_runs["dt_over_4"] = run_passes(2, 0.000125, retain_response=False, end_s=516.0)
385:         for stiffness_mn_m in (100.0, 250.0, 500.0):
386:             regularization_runs[f"kn_{stiffness_mn_m:g}_MN_m"] = run_passes(
387:                 1,
388:                 0.000125,
389:                 retain_response=False,
390:                 end_s=516.0,
391:                 contact_stiffness_n_m=stiffness_mn_m * 1.0e6,
392:             )
393:     report = {
394:         "case_id": "Barge120x50_ThiesProxy_ChronoExplicitContact",
395:         "status": "computed_multibody_partitioned_case_study_not_full_scale_validation",
396:         "same_platform_chain": "120x50x7 HAMS operator + deterministic JONSWAP wave force + Wang plume-force profile truncated at touchdown + four-leg multibody contact",
397:         "algorithms": algorithm_rows,
398:         "iterative_run": {key: value for key, value in iterative.items() if key != "response"},
399:         "coupling_iteration_convergence": coupling_iteration_summary(iterative["passes"]),
400:         "time_step_convergence": convergence_summary(convergence_runs) if convergence_runs else {"enabled": False},
401:         "contact_regularization_sensitivity": (
402:             contact_regularization_summary(regularization_runs) if regularization_runs else {"enabled": False}
403:         ),
404:         "validation_hierarchy": {
405:             "level_1_code_verification": ["action-reaction wrench residual", "mass closure", "contact coefficient-mode audit", "time-step refinement"],
```

## R08_memory_initialization

`analysis/rocket_recovery/chrono_revision_study.py`，原文件第653–704行。

SHA-256 `a012e697c7ff20da5dc369910bf5900fac31ddcbed2815e6f79f9d6ff8c10f52`

```text
653:     restoring_term = np.einsum("ij,j->i", restoring, q)
654:     qdd = np.einsum(
655:         "ij,j->i",
656:         operator.active_mass_inverse,
657:         external_force - damping_term - restoring_term - memory_force,
658:     )
659:     cos_dot = qd[None, :] - operator.omega_rad_s[:, None] * memory[1]
660:     sin_dot = operator.omega_rad_s[:, None] * memory[0]
661:     return np.concatenate([qd, qdd, cos_dot.reshape(-1), sin_dot.reshape(-1)])
662: 
663: 
664: def solve_platform(
665:     operator: PlatformOperator,
666:     config: dict[str, Any],
667:     wang_config: dict[str, Any],
668:     wave: dict[str, Any],
669:     time_s: np.ndarray,
670:     feedback_active: np.ndarray,
671: ) -> dict[str, Any]:
672:     time = np.asarray(time_s, dtype=float)
673:     feedback = np.asarray(feedback_active, dtype=float)
674:     if feedback.shape != (len(time), 3):
675:         raise ValueError(f"Platform feedback must have shape ({len(time)}, 3), got {feedback.shape}.")
676:     wave_force = wave_force_series(time, float(config["time_domain"]["start_s"]), operator, wave)
677:     plume_full = wang_plume_force_6dof(time, wang_config, config)
678:     plume_force = plume_full[:, operator.active_indices]
679:     external = wave_force + plume_force + feedback
680:     ndof = 3
681:     frequency_count = len(operator.omega_rad_s)
682:     state = np.zeros(2 * ndof + 2 * frequency_count * ndof, dtype=float)
683:     q_hist = np.zeros((len(time), ndof), dtype=float)
684:     qd_hist = np.zeros((len(time), ndof), dtype=float)
685:     memory_force_hist = np.zeros((len(time), ndof), dtype=float)
686:     active_radiation = operator.active_radiation()
687:     active_mass = operator.active_matrix(operator.mass)
688:     active_restoring = operator.active_matrix(operator.restoring)
689: 
690:     for index, current_time in enumerate(time):
691:         q_hist[index] = state[:ndof]
692:         qd_hist[index] = state[ndof : 2 * ndof]
693:         memory = state[2 * ndof :].reshape(2, frequency_count, ndof)
694:         memory_force_hist[index] = np.einsum("k,kij,kj->i", operator.radiation_weights, active_radiation, memory[0])
695:         if index == len(time) - 1:
696:             break
697:         h = float(time[index + 1] - current_time)
698:         force_0 = external[index]
699:         force_1 = external[index + 1]
700:         force_half = 0.5 * (force_0 + force_1)
701:         k1 = platform_rhs(state, force_0, operator)
702:         k2 = platform_rhs(state + 0.5 * h * k1, force_half, operator)
703:         k3 = platform_rhs(state + 0.5 * h * k2, force_half, operator)
704:         k4 = platform_rhs(state + h * k3, force_1, operator)
```

## R09_certificate_comparator

`CertTest/test_cert.py`，原文件第1–93行。

SHA-256 `6d45579465ad9308e225230504f788a7523c1ad760d6eba9c545fb219b3e94d8`

```text
1: import unittest
2: import os
3: import glob
4: import math
5: 
6: 
7: REL_TOL = 1.0e-1
8: ABS_TOL = 1.0e-7
9: 
10: def isfloat(instr):
11:     try:
12:         _ = float(instr)
13:         return True
14:     except:
15:         return False
16: 
17:     
18: class TestCertRegression(unittest.TestCase):
19:     def compare_cert(self, cert):
20:         start_dir = os.path.dirname( os.path.realpath(__file__) )
21:         print(f'Running regression tests for {cert} example')
22:         truth_dir = os.path.join(start_dir, cert, 'Output_Benchmark')
23:         actual_dir = os.path.join(start_dir, cert, 'Output')
24:         all_files = glob.glob(os.path.join(truth_dir, '**', '*.*'), recursive=True)
25:         all_files = sorted(os.path.relpath(path, truth_dir) for path in all_files)
26: 
27:         self.assertTrue(all_files, f'No benchmark files found for {cert}')
28:         for relative_file in all_files:
29:             truth_file = os.path.join(truth_dir, relative_file)
30:             actual_file = os.path.join(actual_dir, relative_file)
31:             with self.subTest(cert=cert, file=relative_file):
32:                 self.assertTrue(os.path.exists(actual_file), f'Missing output file: {actual_file}')
33:                 with open(truth_file) as handle:
34:                     truth_data = handle.read().splitlines()
35:                 with open(actual_file) as handle:
36:                     actual_data = handle.read().splitlines()
37: 
38:                 self.assertEqual(len(truth_data), len(actual_data), f'Line count differs for {relative_file}')
39:                 mismatches = []
40:                 for line_index, (truth_line, actual_line) in enumerate(zip(truth_data, actual_data), start=1):
41:                     truth_tokens = truth_line.split()
42:                     actual_tokens = actual_line.split()
43:                     if len(truth_tokens) != len(actual_tokens):
44:                         mismatches.append(
45:                             f'line {line_index}: token count {len(truth_tokens)} vs {len(actual_tokens)}'
46:                         )
47:                         continue
48:                     for token_index, (truth_token, actual_token) in enumerate(zip(truth_tokens, actual_tokens), start=1):
49:                         truth_is_float = isfloat(truth_token)
50:                         actual_is_float = isfloat(actual_token)
51:                         if truth_is_float and actual_is_float:
52:                             truth_value = float(truth_token)
53:                             actual_value = float(actual_token)
54:                             if math.isnan(truth_value) or math.isnan(actual_value):
55:                                 if math.isnan(truth_value) and math.isnan(actual_value):
56:                                     continue
57:                                 mismatches.append(
58:                                     f'line {line_index}, token {token_index}: '
59:                                     f'TRUTH {truth_value} vs NEW {actual_value}'
60:                                 )
61:                                 continue
62:                             if math.isinf(truth_value) or math.isinf(actual_value):
63:                                 if truth_value == actual_value:
64:                                     continue
65:                                 mismatches.append(
66:                                     f'line {line_index}, token {token_index}: '
67:                                     f'TRUTH {truth_value} vs NEW {actual_value}'
68:                                 )
69:                                 continue
70:                             if not math.isclose(
71:                                 truth_value,
72:                                 actual_value,
73:                                 rel_tol=REL_TOL,
74:                                 abs_tol=ABS_TOL,
75:                             ):
76:                                 mismatches.append(
77:                                     f'line {line_index}, token {token_index}: '
78:                                     f'TRUTH {truth_value} vs NEW {actual_value}'
79:                                 )
80:                         elif truth_is_float != actual_is_float:
81:                             mismatches.append(
82:                                 f'line {line_index}, token {token_index}: '
83:                                 f'numeric/text mismatch {truth_token!r} vs {actual_token!r}'
84:                             )
85:                         elif truth_token != actual_token:
86:                             mismatches.append(
87:                                 f'line {line_index}, token {token_index}: '
88:                                 f'{truth_token!r} vs {actual_token!r}'
89:                             )
90:                 self.assertFalse(
91:                     mismatches,
92:                     f'{len(mismatches)} mismatch(es) in {relative_file}; first: {mismatches[0] if mismatches else ""}',
93:                 )
```

## R10_reference_alignment

`analysis/rocket_recovery/yang_2026_landing_identification.py`，原文件第91–132行。

SHA-256 `cb985bbdd1cb2a8a05e2eac6e53b33d3265c59b9a59bc48e16610bfe7abff8c9`

```text
91:     }
92:     acceleration_time, acceleration = read_curve(file_map["acceleration"])
93:     force_time, force = read_curve(file_map["force"])
94:     stroke_time, stroke = read_curve(file_map["stroke"])
95: 
96:     pre_limit = float(np.quantile(force_time, 0.13))
97:     force_baseline = float(np.median(force[force_time <= pre_limit]))
98:     force_corrected = np.maximum(0.0, force - force_baseline)
99:     threshold = 0.08 * max(float(np.max(force_corrected)), 1.0)
100:     contact_candidates = np.where(force_corrected >= threshold)[0]
101:     if not len(contact_candidates):
102:         raise ValueError(f"Could not detect contact in {figure}")
103:     contact_time = float(force_time[int(contact_candidates[0])])
104: 
105:     stroke_pre = stroke[stroke_time <= contact_time]
106:     stroke_baseline_mm = float(np.median(stroke_pre)) if len(stroke_pre) else float(stroke[0])
107:     stroke_corrected_m = np.maximum(0.0, (stroke - stroke_baseline_mm) * 1.0e-3)
108:     return {
109:         "contact_time_s": contact_time,
110:         "acceleration": {
111:             "time_from_contact_s": acceleration_time - contact_time,
112:             "value_m_s2": acceleration * 1.0e-3,
113:             "raw_unit": "mm/s^2",
114:         },
115:         "force": {
116:             "time_from_contact_s": force_time - contact_time,
117:             "value_n": force_corrected,
118:             "baseline_removed_n": force_baseline,
119:         },
120:         "stroke": {
121:             "time_from_contact_s": stroke_time - contact_time,
122:             "value_m": stroke_corrected_m,
123:             "baseline_removed_mm": stroke_baseline_mm,
124:         },
125:     }
126: 
127: 
128: def leg_projected_coordinates(radius_m: float, tilt_axis_deg: float) -> np.ndarray:
129:     azimuths = np.radians(np.asarray([0.0, 90.0, 180.0, 270.0]))
130:     axis = math.radians(float(tilt_axis_deg))
131:     return float(radius_m) * np.cos(azimuths - axis)
132: 
```

## R10_optimizer

`analysis/rocket_recovery/yang_2026_landing_identification.py`，原文件第260–327行。

SHA-256 `cb985bbdd1cb2a8a05e2eac6e53b33d3265c59b9a59bc48e16610bfe7abff8c9`

```text
260:             reference["force"]["time_from_contact_s"],
261:             reference["force"]["value_n"],
262:         ),
263:         "stroke_m": np.interp(
264:             time_s,
265:             reference["stroke"]["time_from_contact_s"],
266:             reference["stroke"]["value_m"],
267:         ),
268:     }
269: 
270: 
271: def calibration_residual(values: np.ndarray, reference: dict[str, Any], sample_time_s: np.ndarray) -> np.ndarray:
272:     parameters = IdentifiedParameters.from_scaled(values)
273:     simulation = simulate_condition("Y0_simultaneous", parameters, dt_s=0.002, duration_s=float(sample_time_s[-1]))
274:     sim_time = simulation["time_s"]
275:     target = reference_on_grid(reference, sample_time_s)
276:     first_leg = 0
277:     simulated = {
278:         "acceleration_up_m_s2": np.interp(sample_time_s, sim_time, simulation["acceleration_up_m_s2"]),
279:         "strut_force_n": np.interp(sample_time_s, sim_time, simulation["strut_force_n"][:, first_leg]),
280:         "stroke_m": np.interp(sample_time_s, sim_time, simulation["stroke_m"][:, first_leg]),
281:     }
282:     weights = {
283:         "acceleration_up_m_s2": 28.0,
284:         "strut_force_n": 100000.0,
285:         "stroke_m": 0.1,
286:     }
287:     residuals = []
288:     for key in ("acceleration_up_m_s2", "strut_force_n", "stroke_m"):
289:         residuals.append((simulated[key] - target[key]) / weights[key])
290:     regularization = np.asarray(
291:         [
292:             (parameters.force_observation_ratio - 0.5) / 0.25,
293:             (parameters.stroke_observation_ratio - 1.0) / 0.5,
294:         ],
295:         dtype=float,
296:     )
297:     return np.concatenate(residuals + [0.03 * regularization])
298: 
299: 
300: def identify_parameters(reference: dict[str, Any]) -> tuple[IdentifiedParameters, dict[str, Any]]:
301:     initial = IdentifiedParameters(
302:         force_observation_ratio=0.5,
303:         stroke_observation_ratio=1.0,
304:         vertical_stiffness_n_m=1.5e5,
305:         quadratic_vertical_stiffness_n_m2=0.0,
306:         compression_vertical_damping_ns_m=2.0e4,
307:         rebound_vertical_damping_ns_m=4.0e4,
308:     )
309:     sample_time = np.linspace(0.0, 1.2, 181)
310:     result = least_squares(
311:         calibration_residual,
312:         initial.to_scaled(),
313:         args=(reference, sample_time),
314:         bounds=(
315:             np.asarray([0.2, 0.3, 0.2, 0.0, 0.1, 0.1]),
316:             np.asarray([0.9, 2.0, 10.0, 20.0, 10.0, 30.0]),
317:         ),
318:         max_nfev=100,
319:         x_scale="jac",
320:         verbose=0,
321:     )
322:     parameters = IdentifiedParameters.from_scaled(result.x)
323:     return parameters, {
324:         "success": bool(result.success),
325:         "status": int(result.status),
326:         "message": result.message,
327:         "cost": float(result.cost),
```