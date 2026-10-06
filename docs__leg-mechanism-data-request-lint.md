# Chrono Real Leg Mechanism Data Request Pack Lint

- Overall status: `pass`
- Pass: `True`
- Generated UTC: `2026-08-08T12:08:55+00:00`
- Request dir: `RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack`
- Checks: `9/9`

## Checks

| ID | Status | Evidence | Blockers |
| --- | --- | --- | --- |
| `request_pack_files_exist` | **PASS** | missing=0, request_dir=RocketRecoveryCases/Chrono_LeggedRecovery/Input/leg_mechanism_data_request_pack |  |
| `todo_headers_match_schema` | **PASS** | header_errors=0 |  |
| `field_tasks_cover_blocking_fields` | **PASS** | tasks=120, blockers=120, missing=0, extra=0, duplicates=0 |  |
| `jsonl_matches_field_tasks` | **PASS** | jsonl_rows=120, csv_rows=120, path_sets_equal=True |  |
| `todo_files_cannot_be_imported_accidentally` | **PASS** | ambiguous_importer_names=0, non_todo_csv=0 |  |
| `todo_rows_cover_blocking_field_groups` | **PASS** | [{"name": "coordinate_system", "expected_count": 3, "actual_count": 3, "missing_count": 0, "extra_count": 0}, {"name": "azimuths", "expected_count": 4, "actual_count": 4, "missing_count": 0, "extra_count": 0}, {"name": "marker_groups", "expected_count": 16, "actual_count": 16, "missing_count": 0, "extra_count": 0}, {"name": "constraint_topology", "expected_count": 24, "actual_count": 24, "missing_count": 0, "extra_count": 0}, {"name": "body_properties", "expected_count": 48, "actual_count": 48, "missing_count": 0, "extra_count": 0}, {"name": "buffer_lock", "expected_count": 5, "actual_count": 5, "missing_count": 0, "extra_count": 0}] |  |
| `todo_rows_are_unfilled` | **PASS** | nonblank_source_cells=0 |  |
| `acceptable_sources_are_strict` | **PASS** | acceptable=['adams_export', 'author_data', 'cad_export', 'calibrated', 'computed_from_source', 'engineering_data', 'measured', 'paper'] |  |
| `current_papers_not_used_to_fill_strict_blockers` | **PASS** | current_papers_can_fill_count=0 |  |

## Coverage

| Group | Expected | Actual | Missing | Extra |
| --- | ---: | ---: | ---: | ---: |
| `coordinate_system` | 3 | 3 | 0 | 0 |
| `azimuths` | 4 | 4 | 0 | 0 |
| `marker_groups` | 16 | 16 | 0 | 0 |
| `constraint_topology` | 24 | 24 | 0 | 0 |
| `body_properties` | 48 | 48 | 0 | 0 |
| `buffer_lock` | 5 | 5 | 0 | 0 |
