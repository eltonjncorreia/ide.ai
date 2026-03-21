# Installation script for ide-ai (Windows PowerShell)
# Usage: .\install-windows.ps1 [-Version latest] [-Destination 'C:\Program Files']

param(
    [string]$Version = "latest",
    [string]$Destination = "$env:LOCALAPPDATA\ide-ai"
)

$ErrorActionPreference = "Stop"

# Create destination directory if it doesn't exist
if (!(Test-Path -Path $Destination)) {
    New-Item -ItemType Directory -Path $Destination | Out-Null
}

# Get download URL
if ($Version -eq "latest") {
    Write-Host "📥 Fetching latest release info..."
    $latestRelease = Invoke-WebRequest -Uri "https://api.github.com/repos/eltonjncorreia/ide.ai/releases/latest" | ConvertFrom-Json
    $downloadUrl = $latestRelease.assets | Where-Object { $_.name -eq "ide-ai-windows-x64.exe" } | Select-Object -ExpandProperty browser_download_url
} else {
    $downloadUrl = "https://github.com/eltonjncorreia/ide.ai/releases/download/v$Version/ide-ai-windows-x64.exe"
}

if (!$downloadUrl) {
    Write-Host "❌ Error: Could not find download URL for ide-ai version $Version" -ForegroundColor Red
    exit 1
}

Write-Host "📥 Downloading ide-ai..."
$exePath = Join-Path $Destination "ide-ai.exe"
Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath

Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "Run '$exePath' to start ide-ai"
Write-Host ""
Write-Host "💡 Tip: Add '$Destination' to your PATH to run 'ide-ai' from anywhere"
