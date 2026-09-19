param(
    [switch]$DryRun,
    [switch]$SkipBuild,
    [switch]$SkipHams,
    [switch]$SkipNargolkar,
    [switch]$SkipWang,
    [switch]$SkipChrono,
    [switch]$FastChrono,
    [switch]$NoServerHint
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$ChronoPython = Join-Path $Root ".tools\chrono-env\python.exe"
$Python = if (Test-Path $ChronoPython) { $ChronoPython } else { "python" }

function Invoke-PipelineStep {
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$Arguments = @()
    )
    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    Write-Host ("    " + $Command + " " + ($Arguments -join " "))
    if (-not $DryRun) {
        & $Command @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Step failed: $Name"
        }
    }
}

Push-Location $Root
try {
    if (-not $SkipBuild) {
        Invoke-PipelineStep "Build HAMS from local SourceCode" "powershell" @(
            "-ExecutionPolicy", "Bypass",
            "-File", ".\local-tools\Build-HAMS.ps1",
            "-NoClean"
        )
    }

    if (-not $SkipNargolkar) {
        Invoke-PipelineStep "Generate Nargolkar 2025 HAMS cases" $Python @(".\analysis\rocket_recovery\nargolkar_2025.py", "generate")
        if (-not $SkipHams) {
            foreach ($caseDir in @(
                ".\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Center",
                ".\RocketRecoveryCases\Paper_Nargolkar_2025\BoxBarge_Offset5m",
                ".\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Center",
                ".\RocketRecoveryCases\Paper_Nargolkar_2025\MARMAC302_Offset30m"
            )) {
                Invoke-PipelineStep "Run HAMS for $caseDir" "powershell" @(
                    "-ExecutionPolicy", "Bypass",
                    "-File", ".\local-tools\Run-HAMS.ps1",
                    "-CaseDir", $caseDir
                )
            }
        }
        Invoke-PipelineStep "Simulate Nargolkar 2025 external dynamics" $Python @(".\analysis\rocket_recovery\nargolkar_2025.py", "simulate")
        Invoke-PipelineStep "Generate Nargolkar 2025 report" $Python @(".\analysis\rocket_recovery\nargolkar_2025.py", "report")
    }

    if (-not $SkipWang) {
        Invoke-PipelineStep "Generate Wang 2023 HAMS case" $Python @(".\analysis\rocket_recovery\wang_2023.py", "generate")
        if (-not $SkipHams) {
            Invoke-PipelineStep "Run HAMS for Wang 2023 case" "powershell" @(
                "-ExecutionPolicy", "Bypass",
                "-File", ".\local-tools\Run-HAMS.ps1",
                "-CaseDir", ".\RocketRecoveryCases\Paper_WangZhi_2023"
            )
        }
        Invoke-PipelineStep "Simulate Wang 2023 Cummins response" $Python @(".\analysis\rocket_recovery\wang_2023.py", "simulate")
        Invoke-PipelineStep "Generate Wang 2023 report" $Python @(".\analysis\rocket_recovery\wang_2023.py", "report")
    }

    if (-not $SkipChrono) {
        Invoke-PipelineStep "Run Chrono one-way landing" $Python @(".\analysis\rocket_recovery\chrono_one_way_recovery.py", "report")
        Invoke-PipelineStep "Write Chrono two-way interface contract" $Python @(".\analysis\rocket_recovery\chrono_two_way_recovery.py", "contract")
        Invoke-PipelineStep "Digitize Thies 2022 absorber curves" $Python @(".\analysis\rocket_recovery\thies_buffer_digitization.py", "report")
        if ($FastChrono) {
            Invoke-PipelineStep "Run Chrono two-way landing, fast no convergence" $Python @(".\analysis\rocket_recovery\chrono_two_way_recovery.py", "report", "--skip-convergence")
            Invoke-PipelineStep "Run Stage 3A tripod, fast case" $Python @(".\analysis\rocket_recovery\chrono_stage3_recovery.py", "report", "--case", "calm_center")
            Invoke-PipelineStep "Run Stage 3A two-way, fast no convergence" $Python @(".\analysis\rocket_recovery\chrono_stage3_two_way_recovery.py", "report", "--case", "calm_center", "--skip-convergence")
            Invoke-PipelineStep "Run Stage 3 lock, fast case" $Python @(".\analysis\rocket_recovery\chrono_stage3_lock_recovery.py", "report", "--case", "calm_center")
            Invoke-PipelineStep "Run Stage 3 lock two-way, fast no convergence" $Python @(".\analysis\rocket_recovery\chrono_stage3_lock_two_way_recovery.py", "report", "--case", "calm_center", "--skip-convergence")
            Invoke-PipelineStep "Run Stage 3A Thies digitized buffer, fast case" $Python @(".\analysis\rocket_recovery\chrono_stage3_thies_buffer_recovery.py", "report", "--case", "calm_center")
        } else {
            Invoke-PipelineStep "Run Chrono two-way landing" $Python @(".\analysis\rocket_recovery\chrono_two_way_recovery.py", "report")
            Invoke-PipelineStep "Run Stage 3A tripod" $Python @(".\analysis\rocket_recovery\chrono_stage3_recovery.py", "report")
            Invoke-PipelineStep "Run Stage 3A two-way" $Python @(".\analysis\rocket_recovery\chrono_stage3_two_way_recovery.py", "report")
            Invoke-PipelineStep "Run Stage 3 lock" $Python @(".\analysis\rocket_recovery\chrono_stage3_lock_recovery.py", "report")
            Invoke-PipelineStep "Run Stage 3 lock two-way" $Python @(".\analysis\rocket_recovery\chrono_stage3_lock_two_way_recovery.py", "report")
            Invoke-PipelineStep "Run Stage 3A Thies digitized buffer" $Python @(".\analysis\rocket_recovery\chrono_stage3_thies_buffer_recovery.py", "report")
        }
        Invoke-PipelineStep "Run Stage 3B rigid-brace diagnostic" $Python @(".\analysis\rocket_recovery\chrono_stage3b_rigid_recovery.py", "report", "--case", "calm_center")
        Invoke-PipelineStep "Run Stage 3C rigid-body-link diagnostic" $Python @(".\analysis\rocket_recovery\chrono_stage3c_rigid_body_link_recovery.py", "report", "--case", "calm_center")
        Invoke-PipelineStep "Write Adams-equivalent leg mechanism data contract" $Python @(".\analysis\rocket_recovery\leg_mechanism_data_contract.py", "report")
        Invoke-PipelineStep "Write CAD/Adams leg mechanism import schema" $Python @(".\analysis\rocket_recovery\leg_mechanism_data_importer.py", "report")
        Invoke-PipelineStep "Run synthetic leg mechanism import self-test" $Python @(".\analysis\rocket_recovery\leg_mechanism_import_selftest.py", "report")
        Invoke-PipelineStep "Run synthetic real-leg Chrono backend self-test" $Python @(".\analysis\rocket_recovery\chrono_real_leg_backend_selftest.py", "report")
        Invoke-PipelineStep "Validate Adams-equivalent leg mechanism data gate" $Python @(".\analysis\rocket_recovery\leg_mechanism_data_validator.py", "report")
        Invoke-PipelineStep "Track real leg mechanism data gaps" $Python @(".\analysis\rocket_recovery\leg_mechanism_gap_tracker.py", "report")
        Invoke-PipelineStep "Write real leg mechanism data request pack" $Python @(".\analysis\rocket_recovery\leg_mechanism_data_request_pack.py", "report")
        Invoke-PipelineStep "Lint real leg mechanism data request pack" $Python @(".\analysis\rocket_recovery\leg_mechanism_data_request_lint.py", "report")
        Invoke-PipelineStep "Gate real Chrono leg mechanism config generation" $Python @(".\analysis\rocket_recovery\real_leg_mechanism_builder.py", "report")
        Invoke-PipelineStep "Gate real Chrono leg mechanism runtime" $Python @(".\analysis\rocket_recovery\chrono_real_leg_mechanism_recovery.py", "report")
    }

    Invoke-PipelineStep "Generate literature comparison registry" $Python @(".\analysis\rocket_recovery\literature_comparison_registry.py", "report")
    Invoke-PipelineStep "Generate model realism audit" $Python @(".\analysis\rocket_recovery\model_realism_audit.py", "report")
    Invoke-PipelineStep "Generate final acceptance audit" $Python @(".\analysis\rocket_recovery\final_acceptance_audit.py", "report")

    if (-not $NoServerHint) {
        Write-Host ""
        Write-Host "Open visualization with:" -ForegroundColor Green
        Write-Host "  cd $Root\visualization"
        Write-Host "  $Python -m http.server 8765 --bind 127.0.0.1"
        Write-Host "  http://127.0.0.1:8765/chrono-final-acceptance.html"
    }
} finally {
    Pop-Location
}
