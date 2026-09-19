param(
    [string]$BasePython = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$envDir = Join-Path $root ".tools\paper-env"
$python = Join-Path $envDir "Scripts\python.exe"
$requirements = Join-Path $root "paper\yang_2026_extension\requirements-paper.txt"

if (-not (Test-Path -LiteralPath $python)) {
    & $BasePython -m venv $envDir
    if ($LASTEXITCODE -ne 0) { throw "Failed to create project-local paper environment." }
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip in the paper environment." }

& $python -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { throw "Failed to install paper dependencies." }

& $python -c "import scienceplots, matplotlib, numpy, scipy, pandas, docx, PIL; print('Paper environment ready:', matplotlib.__version__)"
if ($LASTEXITCODE -ne 0) { throw "Paper environment import check failed." }

Write-Host "Project-local paper environment: $envDir" -ForegroundColor Green
Write-Host "No system PATH or system Python package was modified."
