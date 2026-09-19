param(
  [string]$Prefix = ".tools\chrono-env",
  [string]$PythonVersion = "3.13",
  [string]$ChronoVersion = "10.0.0",
  [string]$CondaCommand = ""
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PrefixPath = Join-Path $Root $Prefix

function Resolve-Conda {
  param([string]$Explicit)
  if ($Explicit) {
    return $Explicit
  }
  $cmd = Get-Command conda.bat -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }
  $candidates = @(
    "E:\Miniconda3\Library\bin\conda.bat",
    "$env:USERPROFILE\miniconda3\Library\bin\conda.bat",
    "$env:USERPROFILE\anaconda3\Library\bin\conda.bat"
  )
  foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
      return $candidate
    }
  }
  throw "conda.bat was not found. Install Miniconda or pass -CondaCommand <path-to-conda.bat>."
}

$Conda = Resolve-Conda $CondaCommand
$env:CONDA_NO_PLUGINS = "true"
Write-Host "Using conda: $Conda"
Write-Host "Project root: $Root"
Write-Host "Chrono env prefix: $PrefixPath"

if (-not (Test-Path $PrefixPath)) {
  & $Conda create --prefix $PrefixPath --override-channels -c conda-forge "python=$PythonVersion" "pychrono=$ChronoVersion" numpy -y
} else {
  & $Conda install --prefix $PrefixPath --override-channels -c conda-forge "pychrono=$ChronoVersion" numpy -y
}

$Python = Join-Path $PrefixPath "python.exe"
& $Python -c "import numpy as np; import pychrono as chrono; print('numpy', np.__version__); print('pychrono', getattr(chrono, '__version__', 'unknown')); print('has ChSystemSMC', hasattr(chrono, 'ChSystemSMC')); print('has ChLinkTSDA', hasattr(chrono, 'ChLinkTSDA'))"
Write-Host "Run Chrono stage 1 with:"
Write-Host "$Python .\analysis\rocket_recovery\chrono_one_way_recovery.py report"
