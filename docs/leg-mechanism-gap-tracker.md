# Chrono Real Leg Mechanism Gap Tracker

- Overall status: `blocked_pending_real_mechanism_data`
- Generated UTC: `2026-08-01T12:52:12+00:00`
- Strict validation ready: `False`
- Blocking fields: `120`
- Current papers can fill blocking fields without new assumption: `0`

## Conclusion

当前论文和 Markdown 可支撑平台水动力、喷流载荷、缓冲器曲线和支腿量级验证，但不能填满 Adams 等价 Chrono 支腿所需的真实 CAD/Adams 机构字段。

No current paper/PDF/Markdown in the workspace provides the full 3D hinge-marker, constraint-topology, mass-property, absorber-topology, and lock-hardware data required to pass the strict real-leg gate.

## Source Matrix

| Source | Useful Data | Cannot Fill | Gate Use |
| --- | --- | --- | --- |
| `Thies_2022` | 火箭高度、直径、着陆质量、质心和惯量<br>四腿 tripod 总体构型<br>B/T/K 高度、PB/PT/PK 长度、33 deg 主腿角、51 deg 斜撑角<br>名义触地速度、触地动能、无摩擦名义工况<br>缓冲器线性刚度/阻尼、表格结果中的行程/力/喷管间隙<br>Figure 4/5 可数字化缓冲器力-行程/力-速度曲线 | 四条腿在火箭体坐标系内的完整 B/T/K/P 三维 marker 坐标<br>真实 CAD/Adams 坐标系原点、轴向和 HAMS 甲板坐标转换<br>每个铰链的 joint type、joint axis、限位和约束图<br>主支柱、斜撑、足垫、缓冲器壳体/活塞/锁紧件的质量、质心和惯量<br>伸缩缓冲器内部拓扑、真实 stroke limit、回弹/伸出行为和锁紧硬件 | `primary_scale_validation_only` |
| `Yue_2022` | 准三维 2-2 / 1-2-1 对称着陆建模方式<br>主支柱力、辅助支柱力、缓冲器行程、加速度的仿真/试验对比指标<br>非线性接触和液体弹簧缓冲器验证思路 | 该文是另一缩比/准三维模型，不是 Thies/RETALT 真实 CAD 数据<br>不能直接填入当前 Thies-based B/T/K/P marker 和质量惯量字段<br>不能替代浮动甲板 HAMS/Cummins 数据 | `future_validation_targets` |
| `Li_2025` | 四腿机构、主支柱、两根辅助支柱、足垫和液气弹簧的建模拓扑描述<br>另一设计的质量/惯量表<br>接触刚度、阻尼、接触半径、接触指数、静/动摩擦系数<br>柔性-刚体耦合和发动机关机后残余推力建模思路 | 这是另一火箭/支腿设计，不能直接填入 Thies/RETALT 机构几何<br>不能与 Thies 几何混合后作为同一真实机构的质量惯量<br>不包含浮式平台水动力或海上甲板运动数据 | `alternate_design_or_contact_reference` |
| `Wang_2023` | JONSWAP 谱 Hs=1.75 m、Tp=4.5 s、gamma=3、浪向 135 deg<br>31 s 喷流载荷时程构造和最终约 20400 kN 的垂向载荷量级<br>165 m x 40 m x 5 m 驳船、四点悬链线系泊、偏心落点响应量级<br>静水/波浪中 heave/roll/pitch 响应文字指标 | 没有火箭四腿结构模型<br>没有足垫接触、缓冲器、摩擦、锁紧或火箭刚体动力学<br>没有 HAMS/Chrono 真实支腿机构所需 CAD/Adams 数据 | `platform_wave_plume_validation` |
| `Nargolkar_2025` | HAMS 势流到 Cummins 时域记忆力再到火箭等效梁/弹簧耦合的主链路<br>箱形驳船和 MARMAC 302 几何/质量参数<br>中心/偏心着陆和不同速度的耦合响应对比 | 该文使用等效弹簧耦合，不是四腿接触模型<br>没有铰链、足垫、缓冲器曲线、摩擦或锁紧硬件<br>不能作为 Adams 等价支腿机构数据来源 | `hydro_structural_coupling_benchmark` |

## Blocking Field Classes

| Class | Count | CSV | Needed Source |
| --- | ---: | --- | --- |
| `coordinate_system` | 3 | `coordinate_system.csv` | CAD/Adams frame export or author frame metadata |
| `azimuths` | 4 | `leg_azimuths.csv` | CAD/Adams leg layout export or published four-leg azimuth table |
| `marker_coordinates` | 36 | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `constraint_topology` | 24 | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `body_properties` | 48 | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `buffer_lock` | 5 | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |
| `unknown` | 0 | `manual_review` | manual review |

## Action Plan

1. `export_frames_and_markers` -> `coordinate_system.csv`, `leg_azimuths.csv`, `marker_coordinates.csv`: validator coordinate_system and geometry_closure checks pass in strict_real_data mode
2. `export_constraint_graph` -> `constraint_topology.csv`: validator constraint_topology check passes and every slider axis is unit length
3. `export_mass_properties` -> `body_properties.csv`: validator body_mass_inertia check passes for main strut, auxiliary struts and footpad of every leg
4. `fill_absorber_and_lock_hardware` -> `buffer_lock.csv`: validator buffer_law and lock_hardware checks pass or lock hardware is explicitly moved to a separate platform-side model
5. `rerun_strict_gate_and_runtime` -> `all`: validator ready=true, builder writes Input/chrono_real_leg_mechanism_config.json, runtime gate runs strict config

## Top Blocking Fields

| Path | Source | CSV | Needed Source |
| --- | --- | --- | --- |
| `coordinate_system.rocket_body_origin` | `missing_required` | `coordinate_system.csv` | CAD/Adams frame export or author frame metadata |
| `coordinate_system.rocket_body_axes` | `missing_required` | `coordinate_system.csv` | CAD/Adams frame export or author frame metadata |
| `coordinate_system.deck_frame_transform` | `missing_required` | `coordinate_system.csv` | CAD/Adams frame export or author frame metadata |
| `legs[0].azimuth_deg` | `engineering_assumption` | `leg_azimuths.csv` | CAD/Adams leg layout export or published four-leg azimuth table |
| `legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.B_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.T_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.K_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].adams_equivalent_geometry.P_footpad_marker_xyz_m.z` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[0].constraint_topology.B_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].constraint_topology.T_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].constraint_topology.K_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].constraint_topology.P_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].constraint_topology.absorber_slider_axis_xyz` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].constraint_topology.joint_limit_definitions` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[0].body_properties.main_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.main_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.main_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.long_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.long_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.long_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.short_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.short_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.short_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.footpad.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.footpad.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[0].body_properties.footpad.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].azimuth_deg` | `engineering_assumption` | `leg_azimuths.csv` | CAD/Adams leg layout export or published four-leg azimuth table |
| `legs[1].adams_equivalent_geometry.B_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.B_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.T_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.T_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.K_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.K_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].adams_equivalent_geometry.P_footpad_marker_xyz_m.z` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[1].constraint_topology.B_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].constraint_topology.T_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].constraint_topology.K_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].constraint_topology.P_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].constraint_topology.absorber_slider_axis_xyz` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].constraint_topology.joint_limit_definitions` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[1].body_properties.main_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.main_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.main_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.long_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.long_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.long_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.short_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.short_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.short_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.footpad.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.footpad.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[1].body_properties.footpad.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].azimuth_deg` | `engineering_assumption` | `leg_azimuths.csv` | CAD/Adams leg layout export or published four-leg azimuth table |
| `legs[2].adams_equivalent_geometry.B_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.B_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.T_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.T_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.K_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.K_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].adams_equivalent_geometry.P_footpad_marker_xyz_m.z` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[2].constraint_topology.B_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].constraint_topology.T_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].constraint_topology.K_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].constraint_topology.P_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].constraint_topology.absorber_slider_axis_xyz` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].constraint_topology.joint_limit_definitions` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[2].body_properties.main_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.main_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.main_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.long_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.long_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.long_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.short_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.short_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.short_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.footpad.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.footpad.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[2].body_properties.footpad.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].azimuth_deg` | `engineering_assumption` | `leg_azimuths.csv` | CAD/Adams leg layout export or published four-leg azimuth table |
| `legs[3].adams_equivalent_geometry.B_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.B_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.T_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.T_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.K_rocket_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.K_rocket_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.P_footpad_marker_xyz_m.x` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.P_footpad_marker_xyz_m.y` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].adams_equivalent_geometry.P_footpad_marker_xyz_m.z` | `missing_required` | `marker_coordinates.csv` | CAD/Adams marker export for B/T/K/P in a declared rocket body frame |
| `legs[3].constraint_topology.B_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].constraint_topology.T_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].constraint_topology.K_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].constraint_topology.P_joint_type` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].constraint_topology.absorber_slider_axis_xyz` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].constraint_topology.joint_limit_definitions` | `missing_required` | `constraint_topology.csv` | Adams constraint graph, CAD mate definitions, or author topology table |
| `legs[3].body_properties.main_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.main_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.main_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.long_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.long_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.long_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.short_auxiliary_strut.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.short_auxiliary_strut.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.short_auxiliary_strut.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.footpad.mass_kg` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.footpad.com_xyz_m` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `legs[3].body_properties.footpad.inertia_kg_m2` | `missing_required` | `body_properties.csv` | CAD mass-property export or validated component mass budget |
| `buffer_law.stroke_limit_m` | `missing_required` | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |
| `buffer_law.extension_behavior` | `missing_required` | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |
| `lock_hardware.mechanism_type` | `missing_required` | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |
| `lock_hardware.trigger_logic` | `missing_required` | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |
| `lock_hardware.constraint_stiffness` | `missing_required` | `buffer_lock.csv` | absorber hardware specification, force-law table, stroke/rebound data, and lock hardware data |

## Commands

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_validator.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\real_leg_mechanism_builder.py report --input .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_data_imported.json
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\chrono_real_leg_mechanism_recovery.py report
```
