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

$allFiles = @()
foreach ($ext in $extensions) {
    $files = Get-ChildItem -LiteralPath $repoRoot -Recurse -Include $ext -File -ErrorAction SilentlyContinue
    $allFiles += $files
}

$totalFiles = $allFiles.Count
Write-Host "Found $totalFiles files to copy."

$copiedFolders = @{}
$copiedFiles = @()
$copiedCount = 0

foreach ($file in $allFiles) {
    $relativePath = $file.FullName.Substring($repoRoot.Length).TrimStart('\', '/')
    $targetPath = Join-Path $targetDir $relativePath
    $targetFolder = Split-Path -Parent $targetPath

    if (-not (Test-Path -LiteralPath $targetFolder)) {
        New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null
        $copiedFolders[$targetFolder] = $true
    }

    Copy-Item -LiteralPath $file.FullName -Destination $targetPath -Force
    $copiedCount++
    $percent = [math]::Round(($copiedCount / $totalFiles) * 100)
    Write-Host "  [$copiedCount/$totalFiles] Copied: $relativePath" -ForegroundColor Green
    $copiedFiles += $relativePath
}

if ($copiedFiles.Count -eq 0) {
    Write-Host "No source files found to copy."
    return
}

Write-Host "Packaging $($copiedFiles.Count) files into flow.zip..."

$topLevelFolders = @{}
foreach ($relativePath in $copiedFiles) {
    $firstFolder = ($relativePath -split '[\\/]')[0]
    if ($firstFolder -and -not $topLevelFolders.ContainsKey($firstFolder)) {
        $topLevelFolders[$firstFolder] = Join-Path $targetDir $firstFolder
    }
}

$folderCount = $topLevelFolders.Count
$currentFolder = 0

if ($topLevelFolders.Count -gt 0) {
    foreach ($folder in $topLevelFolders.Values) {
        $currentFolder++
        $percent = [math]::Round(($currentFolder / $folderCount) * 100)
        Write-Host "  Packaging folder [$currentFolder/$folderCount]: $folder" -ForegroundColor Cyan
    }
    $archivePaths = $topLevelFolders.Values
    Compress-Archive -Path $archivePaths -DestinationPath $zipFile -Force
}
else {
    Compress-Archive -Path "$targetDir\*" -DestinationPath $zipFile -Force
}

Write-Host "Packaging complete." -ForegroundColor Green

Write-Host "Cleaning up intermediate files..."

$cleanupCount = 0
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
    $cleanupCount++
    Write-Host "  [$cleanupCount/$($copiedFiles.Count)] Removed: $relativePath" -ForegroundColor Yellow
}

Write-Host "Done. Created: $zipFile"