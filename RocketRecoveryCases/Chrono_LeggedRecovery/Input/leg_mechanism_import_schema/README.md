# Leg Mechanism Import Schema

Fill these CSV files only with CAD, Adams export, author data, calibrated engineering data, or measured data.
Do not use the current proxy assumptions as imported data.

Accepted source categories for validator-ready fields include:
`paper`, `cad_export`, `adams_export`, `author_data`, `measured`, `calibrated`, `computed_from_source`, `engineering_data`.

Run:

```powershell
.\.tools\chrono-env\python.exe .\analysis\rocket_recovery\leg_mechanism_data_importer.py import --source-dir .\RocketRecoveryCases\Chrono_LeggedRecovery\Input\leg_mechanism_import_schema
```
