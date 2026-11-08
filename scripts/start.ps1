$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw 'Virtual environment missing. Follow the installation commands in README.md.'
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'web\index.html') -PathType Leaf)) {
    throw 'Web interface missing. Check that the complete project source is present.'
}
Push-Location -LiteralPath $projectRoot
try {
    Write-Host 'Prooflane: http://127.0.0.1:8765 (Ctrl+C to stop)'
    & $pythonPath -m uvicorn prooflane.app:app --host 127.0.0.1 --port 8765
    if ($LASTEXITCODE -ne 0) {
        throw "Prooflane exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
