# Chrono Real Leg Mechanism Data Request Pack

These files are a data-acquisition checklist. They are not imported automatically.
Copy completed and source-tagged rows into `Input/leg_mechanism_import_schema/*.csv` only after the source data are available.

Accepted source categories:
`cad_export`, `adams_export`, `author_data`, `measured`, `calibrated`, `paper`, `computed_from_source`, `engineering_data`

Do not use `synthetic_test_fixture`, `engineering_assumption`, `implementation_proxy`, or blank source tags for strict validation.
- `field_tasks.csv`: Master task list for every strict blocking field. rows=120
- `coordinate_system.todo.csv`: Fill with rocket/deck frame metadata, then copy validated rows into coordinate_system.csv. rows=3
- `leg_azimuths.todo.csv`: Fill with real four-leg azimuths. rows=4
- `marker_coordinates.todo.csv`: Fill with B/T/K/P marker coordinates from one declared frame. rows=16
- `constraint_topology.todo.csv`: Fill with joint types, axes, limits, and slider definitions. rows=24
- `body_properties.todo.csv`: Fill with CAD mass, COM, and inertia tensors. rows=48
- `buffer_lock.todo.csv`: Fill with absorber stroke/rebound behavior and lock hardware data. rows=5
