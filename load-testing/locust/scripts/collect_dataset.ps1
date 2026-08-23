param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("normal", "ramp", "spike", "heavy")]
    [string]$Scenario,

    [string]$HostUrl = "http://localhost:5000",
    [string]$PrometheusUrl = "http://localhost:9090",
    [switch]$Reset
)

$scriptDir = $PSScriptRoot
$outputPath = Join-Path $scriptDir "..\dataset_exports"
$datasetCsv = Join-Path $outputPath "monitoring_dataset.csv"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$locustPrefix = Join-Path $outputPath "${timestamp}_${Scenario}_locust"

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

if ($Reset -and (Test-Path $datasetCsv)) {
    Remove-Item -Force $datasetCsv
}

$env:LOCUST_SCENARIO = $Scenario
$start = Get-Date

Write-Host "Running scenario: $Scenario"
Write-Host "Start time: $($start.ToString('o'))"

locust -f (Join-Path $scriptDir "locustfile.py") --host $HostUrl --headless --csv $locustPrefix --exit-code-on-error 0

if ($LASTEXITCODE -ne 0) {
    throw "Locust failed for scenario '$Scenario'."
}

$end = Get-Date

Write-Host "End time: $($end.ToString('o'))"

python (Join-Path $scriptDir "export_prometheus_dataset.py") `
    --prom-url $PrometheusUrl `
    --scenario $Scenario `
    --start $start.ToString("o") `
    --end $end.ToString("o") `
    --output $datasetCsv `
    --append

if ($LASTEXITCODE -ne 0) {
    throw "Prometheus export failed for scenario '$Scenario'."
}

Write-Host "Updated dataset: $datasetCsv"
