param(
    [string]$Python = "",
    [double]$DeckDurationSeconds = 120.0,
    [double]$DeckTimeStepSeconds = 0.01,
    [int]$DeckSeed = 2026
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$localPaperPython = Join-Path $root ".tools\paper-env\Scripts\python.exe"
if ([string]::IsNullOrWhiteSpace($Python)) {
    $Python = if (Test-Path -LiteralPath $localPaperPython) { $localPaperPython } else { "python" }
}
$paperBase = "Analysis+of+Sea-Based+Landing+Dynamics+of+Reusable+Landing+Vehicle+Considering+Mechanism+Flexibility"
$sourcePdfItem = Get-ChildItem -Path $root -Recurse -File -Filter "$paperBase.pdf" | Select-Object -First 1
$sourcePdf = if ($null -eq $sourcePdfItem) { $null } else { $sourcePdfItem.FullName }
$renderDir = Join-Path $root "RocketRecoveryCases\Paper_Yang_2026\reference\renders"
$renderPrefix = Join-Path $renderDir "yang-2026-page-07-160dpi"
$poppler = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe"

if ($null -eq $sourcePdf -or -not (Test-Path -LiteralPath $sourcePdf)) {
    throw "Yang 2026 source PDF not found: $sourcePdf"
}
if (-not (Test-Path -LiteralPath $poppler)) {
    throw "Bundled Poppler pdftoppm not found: $poppler"
}

New-Item -ItemType Directory -Path $renderDir -Force | Out-Null

Push-Location $root
try {
    & $Python ".\analysis\rocket_recovery\yang_2026.py" report --duration $DeckDurationSeconds --dt $DeckTimeStepSeconds --seed $DeckSeed
    if ($LASTEXITCODE -ne 0) { throw "Yang evidence report failed." }

    & $poppler -f 7 -l 7 -singlefile -png -r 160 $sourcePdf $renderPrefix
    if ($LASTEXITCODE -ne 0) { throw "Yang PDF rendering failed." }

    & $Python ".\analysis\rocket_recovery\yang_2026_digitize.py"
    if ($LASTEXITCODE -ne 0) { throw "Yang curve digitization failed." }

    & $Python ".\analysis\rocket_recovery\yang_2026_landing_identification.py" report
    if ($LASTEXITCODE -ne 0) { throw "Yang reduced landing-model identification failed." }

    & $Python ".\analysis\rocket_recovery\barge_wave_sensitivity.py" report --seeds 100 --seed-start 202600 --duration 600 --dt 0.1
    if ($LASTEXITCODE -ne 0) { throw "HAMS barge wave-sensitivity calculation failed." }

    & $Python ".\analysis\rocket_recovery\yang_2026_figures.py"
    if ($LASTEXITCODE -ne 0) { throw "Yang paper figure generation failed." }

    & $Python ".\analysis\rocket_recovery\literature_comparison_registry.py" registry
    if ($LASTEXITCODE -ne 0) { throw "Literature registry generation failed." }

    & $Python -m unittest analysis.rocket_recovery.test_recovery_tools analysis.rocket_recovery.test_yang_2026 analysis.rocket_recovery.test_yang_2026_landing_identification analysis.rocket_recovery.test_barge_wave_sensitivity -v
    if ($LASTEXITCODE -ne 0) { throw "Yang paper pipeline tests failed." }
}
finally {
    Pop-Location
}

Write-Host "Yang 2026 evidence pipeline completed."
Write-Host "Manuscript: $root\paper\yang_2026_extension\manuscript.md"
Write-Host "Evidence report: $root\RocketRecoveryCases\Paper_Yang_2026\yang-2026-evidence-report.json"
Write-Host "Digitized data: $root\RocketRecoveryCases\Paper_Yang_2026\reference\digitized"
Write-Host "Paper figures: $root\paper\yang_2026_extension\figures"
Write-Host "Wave sensitivity: $root\RocketRecoveryCases\Barge_120x50\Output\RocketRecovery\wave-sensitivity.json"
