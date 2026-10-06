param([string]$OutputDir = "RocketRecoveryCases/Chrono_LeggedRecovery_Corrected20260927_v2", [switch]$Resume)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Prefix = Join-Path $Root ".tools/chrono-env"
$OldPath = $env:PATH
$OldBlas = $env:OPENBLAS_NUM_THREADS
$OldOmp = $env:OMP_NUM_THREADS
$OldEncoding = $env:PYTHONIOENCODING
Push-Location $Root
try {
    # Conda's native LAPACK/Chrono DLLs must come from the same local prefix.
    $env:PATH = "$Prefix;$Prefix\Library\bin;$Prefix\Scripts;$OldPath"
    $env:OPENBLAS_NUM_THREADS = "1"
    $env:OMP_NUM_THREADS = "1"
    $env:PYTHONIOENCODING = "utf-8"
    $EvidenceDir = if ($Resume) { Join-Path $OutputDir ("resume-environment-" + (Get-Date -Format "yyyyMMdd-HHmmss")) } else { $OutputDir }
    & "$Prefix/python.exe" -m analysis.rocket_recovery.corrected_contact_evidence capture --case $EvidenceDir
    if ($LASTEXITCODE -ne 0) { throw "Environment capture failed" }
    $RunArgs = @("-u", "-m", "analysis.rocket_recovery.chrono_same_platform_multibody", "--output-dir", $OutputDir)
    if ($Resume) { $RunArgs += "--resume" }
    & "$Prefix/python.exe" @RunArgs
    if ($LASTEXITCODE -ne 0) { throw "Corrected contact run failed: $LASTEXITCODE" }
    & "$Prefix/python.exe" -m analysis.rocket_recovery.corrected_contact_evidence audit --case $OutputDir
    if ($LASTEXITCODE -ne 0) { throw "Output audit failed" }
} finally {
    $env:PATH = $OldPath
    $env:OPENBLAS_NUM_THREADS = $OldBlas
    $env:OMP_NUM_THREADS = $OldOmp
    $env:PYTHONIOENCODING = $OldEncoding
    Pop-Location
}
