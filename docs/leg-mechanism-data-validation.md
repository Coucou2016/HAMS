# Chrono Leg Mechanism Data Validation

- Overall status: `incomplete_for_adams_equivalent_chrono_model`
- Ready: `False`
- Validation mode: `strict_real_data`
- Input: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_template.json`
- Generated UTC: `2026-08-01T12:51:45+00:00`
- Checks: `0/7` passing
- Blocking fields: `120`

## Checks

| ID | Status | Evidence | Blockers |
| --- | --- | --- | --- |
| required_field_sources | **CHECK** | required=180, missing=116, blocking_source=120 | coordinate_system.rocket_body_origin, coordinate_system.rocket_body_axes, coordinate_system.deck_frame_transform, legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.x, legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.y, legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.x, legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.y, legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.x, legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.y, legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.x, ... 70 more |
| coordinate_system | **MISSING** | 3 coordinate-system fields are missing or blocked | coordinate_system.rocket_body_origin, coordinate_system.rocket_body_axes, coordinate_system.deck_frame_transform |
| geometry_closure | **MISSING** | 4 leg geometry checks are blocked | leg_1: missing B/T/K/P 3D marker coordinates, leg_2: missing B/T/K/P 3D marker coordinates, leg_3: missing B/T/K/P 3D marker coordinates, leg_4: missing B/T/K/P 3D marker coordinates |
| constraint_topology | **MISSING** | 24 topology fields are missing or blocked | legs[0].constraint_topology.B_joint_type, legs[0].constraint_topology.T_joint_type, legs[0].constraint_topology.K_joint_type, legs[0].constraint_topology.P_joint_type, legs[0].constraint_topology.absorber_slider_axis_xyz, legs[0].constraint_topology.joint_limit_definitions, legs[1].constraint_topology.B_joint_type, legs[1].constraint_topology.T_joint_type, legs[1].constraint_topology.K_joint_type, legs[1].constraint_topology.P_joint_type, ... 14 more |
| body_mass_inertia | **MISSING** | 48 body-property fields are missing or blocked | legs[0].body_properties.main_strut.mass_kg, legs[0].body_properties.main_strut.com_xyz_m, legs[0].body_properties.main_strut.inertia_kg_m2, legs[0].body_properties.long_auxiliary_strut.mass_kg, legs[0].body_properties.long_auxiliary_strut.com_xyz_m, legs[0].body_properties.long_auxiliary_strut.inertia_kg_m2, legs[0].body_properties.short_auxiliary_strut.mass_kg, legs[0].body_properties.short_auxiliary_strut.com_xyz_m, legs[0].body_properties.short_auxiliary_strut.inertia_kg_m2, legs[0].body_properties.footpad.mass_kg, ... 38 more |
| buffer_law | **PARTIAL** | table_exists=True, blockers=2 | buffer_law.stroke_limit_m, buffer_law.extension_behavior |
| lock_hardware | **MISSING** | 3 lock fields are missing or blocked | lock_hardware.mechanism_type, lock_hardware.trigger_logic, lock_hardware.constraint_stiffness |

## Geometry Checks

- `leg_1`: MISSING missing marker coordinates
- `leg_2`: MISSING missing marker coordinates
- `leg_3`: MISSING missing marker coordinates
- `leg_4`: MISSING missing marker coordinates

## Gate

Keep using Stage 3A proxy/diagnostic branches; do not build or claim an Adams-equivalent Chrono mechanism from this data.
