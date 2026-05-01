$ErrorActionPreference = "Stop"

Write-Host "Running copy_src script: $PSCommandPath"

$scriptDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $scriptDir
$targetDir = (Get-Location).Path
$zipFile = Join-Path $targetDir "flow.zip"

if (Test-Path -LiteralPath $zipFile) {
    Write-Host "Removing existing zip file: $zipFile"
    Remove-Item -LiteralPath $zipFile -Force
}

$extensions = @("*.py", "*.ipynb")

Write-Host "Copying source files from: $repoRoot"
Write-Host "To target folder: $targetDir"

$copiedFolders = @{}
$copiedFiles = @()

foreach ($ext in $extensions) {
    $files = Get-ChildItem -LiteralPath $repoRoot -Recurse -Include $ext -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($repoRoot.Length).TrimStart('\', '/')
        $targetPath = Join-Path $targetDir $relativePath
        $targetFolder = Split-Path -Parent $targetPath

        if (-not (Test-Path -LiteralPath $targetFolder)) {
            New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null
            $copiedFolders[$targetFolder] = $true
        }

        Copy-Item -LiteralPath $file.FullName -Destination $targetPath -Force
        Write-Host "  Copied: $relativePath"
        $copiedFiles += $relativePath
    }
}

if ($copiedFiles.Count -eq 0) {
    Write-Host "No source files found to copy."
    return
}

Write-Host "Packaging $($copiedFiles.Count) files into flow.zip..."

$archivePaths = @()
foreach ($relativePath in $copiedFiles) {
    $targetPath = Join-Path $targetDir $relativePath
    $archivePaths += $targetPath
}

Compress-Archive -Path $archivePaths -DestinationPath $zipFile -Force

Write-Host "Cleaning up intermediate files..."

foreach ($relativePath in $copiedFiles) {
    $targetPath = Join-Path $targetDir $relativePath
    if (Test-Path -LiteralPath $targetPath) {
        Remove-Item -LiteralPath $targetPath -Force
        $folder = Split-Path -Parent $targetPath
        $remainingFiles = Get-ChildItem -LiteralPath $folder -File -ErrorAction SilentlyContinue
        if ($remainingFiles.Count -eq 0) {
            Remove-Item -LiteralPath $folder -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "Done. Created: $zipFile"