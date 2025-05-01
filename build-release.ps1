# Set paths
$sourcePath = "J:\git projects\linguaforge"
$releaseDir = "J:\git releases"
$stagingDir = "$releaseDir\LinguaForge_1.0"
$zipPath = "$releaseDir\LinguaForge-1.0-windows.zip"

# Ensure release directory exists
if (-not (Test-Path $releaseDir)) {
    New-Item -ItemType Directory -Path $releaseDir | Out-Null
}

# Clean up previous staging folder if it exists
if (Test-Path $stagingDir) {
    Remove-Item -Recurse -Force $stagingDir
}

# Copy project files
Copy-Item -Recurse -Path "$sourcePath\*" -Destination $stagingDir

# Remove unnecessary folders
$excluded = @("model", "logs", "temp", "input", "translated-output", "built-srt", ".git", ".vscode", "__pycache__", "config.json", "*.zip")
foreach ($item in $excluded) {
    Get-ChildItem -Path $stagingDir -Include $item -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
}

# Create the zip archive
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path "$stagingDir\*" -DestinationPath $zipPath

Write-Host "`n✅ Release zip created at: $zipPath"
