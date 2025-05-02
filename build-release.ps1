# build-release.ps1
$env:PYTHONOPTIMIZE = "2"
Remove-Item -Recurse -Force dist, build, *.spec -ErrorAction SilentlyContinue

pyinstaller LinguaForge.py `
    --name LinguaForge `
    --noconsole `
    --onefile `
    --icon=icon.ico `
    --add-data "bin;bin" `
    --add-data "model;model" `
    --add-data "theme;theme" `
    --add-data "engine;engine" `
    --hidden-import customtkinter

Write-Host "Build complete. EXE is in dist\LinguaForge.exe"
