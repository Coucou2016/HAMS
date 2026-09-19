# Chrono Leg Mechanism Data Contract

- Overall status: `incomplete_for_adams_equivalent_chrono_model`
- Generated UTC: `2026-08-01T11:24:11+00:00`
- Template: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_template.json`
- Blocking requirements: `8`
- Blocking fields: `120`

## Purpose

This contract defines the data needed to replace the current Stage 3A/3B/3C proxy legs with an Adams-equivalent Project Chrono mechanism.
It intentionally keeps the current model incomplete for Adams equivalence until real hinge, topology, body-property, absorber, and lock data are supplied.

## Requirements

| ID | Component | Status | Evidence | Next action |
| --- | --- | --- | --- | --- |
| coordinate_system_body_frame | coordinate_system | **partially_available** | Project HAMS/Cummins deck frame is defined; the Thies/Adams rocket leg CAD frame is not published. | Use the CAD/Adams export frame or author-provided frame metadata; record any transform into the HAMS deck frame. |
| leg_azimuths | geometry | **engineering_assumption** | Current model assumes symmetric 45/135/225/315 deg azimuths. | Replace the assumed azimuths with CAD or paper values. |
| joint_coordinates_b_t_k_p | geometry | **partially_available** | Thies Table 4 gives B/T/K heights and PT/KP/PB lengths; full x/y/z hinge coordinates are not available. | Export hinge marker coordinates from CAD/Adams or obtain author tables. |
| joint_types_and_axes | topology | **missing_required** | The papers show the tripod concept but not the Adams constraint graph. | Define the exact Chrono constraint graph from CAD/Adams topology before claiming Adams equivalence. |
| telescopic_absorber_topology | absorber | **missing_required** | Only stiffness/damping/table curves and reference deformation are available; internal multi-body topology is not published. | Add absorber CAD/Adams markers and measured force law metadata. |
| body_masses_inertias | dynamics | **missing_required** | Stage 3C uses explicit placeholder rod masses/inertias only as a failed diagnostic. | Use CAD mass properties or validated engineering mass budget per component. |
| force_stroke_velocity_curves | absorber | **available_digitized** | Thies Figure 4/5 raster curves have been digitized and connected to a Chrono table buffer branch. | Prefer original author tables or measured hardware data when available; keep raster digitization uncertainty recorded. |
| footpad_contact_material | contact | **engineering_assumption** | Current model uses Li 2025 contact values and explicit material assumptions, not Thies-specific hardware data. | Replace with measured footpad/deck values or a calibrated contact model. |
| lock_hardware | lock | **implementation_proxy** | Current Stage 3 lock uses ChLinkMateFix as a proxy after stability criteria are met. | Add actual post-landing securing hardware or define this as a separate platform-side model. |
| validation_curves | validation | **partially_available** | Current registry contains table-scale checks and digitized buffer curves; many full dynamic curves remain gaps. | Digitize the remaining figures or obtain source data for pointwise validation. |

## Blocking Fields

- `coordinate_system.rocket_body_origin`: Use CAD/Adams exported frame origin.
- `coordinate_system.rocket_body_axes`: Use CAD/Adams exported axis convention.
- `coordinate_system.deck_frame_transform`: Rigid transform from rocket landing frame to HAMS/Cummins deck frame.
- `legs[0].azimuth_deg`: Symmetric azimuth used by the current Chrono proxy; not a published Thies value.
- `legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.x`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.y`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.z`: Footpad joint height relative to pad/contact geometry is not published.
- `legs[0].constraint_topology.B_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[0].constraint_topology.T_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[0].constraint_topology.K_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[0].constraint_topology.P_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[0].constraint_topology.absorber_slider_axis_xyz`: Required if the main leg is telescopic.
- `legs[0].constraint_topology.joint_limit_definitions`: Required for stops, deployment locks, and post-touchdown constraints.
- `legs[0].body_properties.main_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[0].body_properties.main_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[0].body_properties.main_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[0].body_properties.long_auxiliary_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[0].body_properties.long_auxiliary_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[0].body_properties.long_auxiliary_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[0].body_properties.short_auxiliary_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[0].body_properties.short_auxiliary_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[0].body_properties.short_auxiliary_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[0].body_properties.footpad.mass_kg`: Current 80 kg value is an engineering placeholder, not paper data.
- `legs[0].body_properties.footpad.com_xyz_m`: CAD/Adams body COM not published.
- `legs[0].body_properties.footpad.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[1].azimuth_deg`: Symmetric azimuth used by the current Chrono proxy; not a published Thies value.
- `legs[1].adams_equivalent_geometry.B_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.B_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.T_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.T_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.K_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.K_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.x`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.y`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.z`: Footpad joint height relative to pad/contact geometry is not published.
- `legs[1].constraint_topology.B_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[1].constraint_topology.T_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[1].constraint_topology.K_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[1].constraint_topology.P_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[1].constraint_topology.absorber_slider_axis_xyz`: Required if the main leg is telescopic.
- `legs[1].constraint_topology.joint_limit_definitions`: Required for stops, deployment locks, and post-touchdown constraints.
- `legs[1].body_properties.main_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[1].body_properties.main_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[1].body_properties.main_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[1].body_properties.long_auxiliary_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[1].body_properties.long_auxiliary_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[1].body_properties.long_auxiliary_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[1].body_properties.short_auxiliary_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[1].body_properties.short_auxiliary_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[1].body_properties.short_auxiliary_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[1].body_properties.footpad.mass_kg`: Current 80 kg value is an engineering placeholder, not paper data.
- `legs[1].body_properties.footpad.com_xyz_m`: CAD/Adams body COM not published.
- `legs[1].body_properties.footpad.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[2].azimuth_deg`: Symmetric azimuth used by the current Chrono proxy; not a published Thies value.
- `legs[2].adams_equivalent_geometry.B_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.B_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.T_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.T_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.K_rocket_marker_xyz_m.x`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.K_rocket_marker_xyz_m.y`: Not published in the current paper extraction.
- `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.x`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.y`: The proxy derives a footprint radius, but real CAD P coordinates are not published.
- `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.z`: Footpad joint height relative to pad/contact geometry is not published.
- `legs[2].constraint_topology.B_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[2].constraint_topology.T_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[2].constraint_topology.K_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[2].constraint_topology.P_joint_type`: Required for a Chrono/Adams-equivalent linkage.
- `legs[2].constraint_topology.absorber_slider_axis_xyz`: Required if the main leg is telescopic.
- `legs[2].constraint_topology.joint_limit_definitions`: Required for stops, deployment locks, and post-touchdown constraints.
- `legs[2].body_properties.main_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[2].body_properties.main_strut.com_xyz_m`: CAD/Adams body COM not published.
- `legs[2].body_properties.main_strut.inertia_kg_m2`: CAD/Adams inertia tensor not published.
- `legs[2].body_properties.long_auxiliary_strut.mass_kg`: CAD/Adams body mass not published.
- `legs[2].body_properties.long_auxiliary_strut.com_xyz_m`: CAD/Adams body COM not published.
- ... 40 more rows in the JSON report.

## Use

1. Fill `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_template.json` from CAD, Adams export, author data, or calibrated measurements.
2. Keep each value's `source_category` and `source_detail` explicit.
3. Replace Stage 3A proxy geometry only after the blocking rows are no longer assumptions or missing values.
