param(
    [ValidateSet("Build", "Start", "Stop", "Status", "Logs", "Analyze")]
    [string]$Action = "Status",

    [ValidateSet("default", "whois-only", "rdap-only")]
    [string]$Mode = "default",

    [ValidateRange(0, 86400)]
    [int]$IntervalSeconds = 60,

    [ValidateRange(1, 1000)]
    [int]$MaxDomains = 100,

    [ValidateRange(0, 1000000)]
    [int]$ForceGcEvery = 0
)

$ErrorActionPreference = "Stop"
$Image = "whoisdomain-memory-soak:local"
$Container = "whoisdomain-memory-soak-$Mode"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ResultsDir = Join-Path $ProjectDir "results-$Mode"

function Build-Image {
    docker build --pull --tag $Image $ProjectDir
    if ($LASTEXITCODE -ne 0) { throw "docker build failed" }
}

switch ($Action) {
    "Build" {
        Build-Image
    }
    "Start" {
        Build-Image
        $Existing = docker ps -a --filter "name=^/$Container$" --format "{{.Names}}"
        if ($Existing -eq $Container) {
            throw "Container $Container already exists. Run Stop first."
        }
        if (Test-Path (Join-Path $ResultsDir "metrics.csv")) {
            $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $ArchivedResultsDir = "${ResultsDir}-${Timestamp}"
            Move-Item -Path $ResultsDir -Destination $ArchivedResultsDir
            Write-Host "Previous results archived: $ArchivedResultsDir"
        }
        New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
        docker run --detach `
            --name $Container `
            --memory 1g `
            --cpus 1 `
            --restart no `
            --env "MODE=$Mode" `
            --env "QUERY_INTERVAL_SECONDS=$IntervalSeconds" `
            --env "MAX_DOMAINS=$MaxDomains" `
            --env "FORCE_GC_EVERY=$ForceGcEvery" `
            --volume "${ResultsDir}:/results" `
            $Image
        if ($LASTEXITCODE -ne 0) { throw "docker run failed" }
        Write-Host "Started $Container"
        Write-Host "Metrics: $ResultsDir\metrics.csv"
        Write-Host "Follow logs: .\run-test.ps1 -Action Logs -Mode $Mode"
    }
    "Stop" {
        docker stop --time 30 $Container
        docker rm $Container
    }
    "Status" {
        docker ps -a --filter "name=^/$Container$"
        docker stats --no-stream $Container
    }
    "Logs" {
        docker logs --follow --tail 100 $Container
    }
    "Analyze" {
        $Metrics = Join-Path $ResultsDir "metrics.csv"
        if (-not (Test-Path $Metrics)) { throw "Missing $Metrics" }
        docker run --rm `
            --entrypoint python3 `
            --volume "${ProjectDir}:/work" `
            --workdir /work `
            $Image /work/analyze.py "/work/results-$Mode/metrics.csv"
    }
}
