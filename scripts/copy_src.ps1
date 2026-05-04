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

# Define required root files
$requiredRootFiles = @(
    "environment.yml",
    "pyproject.toml",
    "README.md"
)

# Copy required root files
foreach ($file in $requiredRootFiles) {
    $sourcePath = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        throw "Required root file not found: $sourcePath"
    }
    Copy-Item -LiteralPath $sourcePath -Destination $targetDir -Force
    Write-Host "  Copied root file: $file" -ForegroundColor Green
}

# Copy the script itself
$scriptSource = Join-Path $scriptDir "copy_src.ps1"
if (Test-Path -LiteralPath $scriptSource) {
    $scriptsTargetDir = Join-Path $targetDir "scripts"
    if (-not (Test-Path -LiteralPath $scriptsTargetDir)) {
        New-Item -ItemType Directory -Path $scriptsTargetDir -Force | Out-Null
    }
    Copy-Item -LiteralPath $scriptSource -Destination $scriptsTargetDir -Force
    Write-Host "  Copied script: scripts/copy_src.ps1" -ForegroundColor Green
}

# Copy source files (py, ipynb)
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
    Write-Host "  [$copiedCount/$totalFiles] Copied: $relativePath" -ForegroundColor Green
    $copiedFiles += $relativePath
}

if ($copiedFiles.Count -eq 0 -and $requiredRootFiles.Count -eq 0) {
    Write-Host "No files found to copy."
    return
}

Write-Host "Packaging files into flow.zip..."

$topLevelFolders = @{}
foreach ($relativePath in $copiedFiles) {
    $firstFolder = ($relativePath -split '[\\/]')[0]
    if ($firstFolder -and -not $topLevelFolders.ContainsKey($firstFolder)) {
        $topLevelFolders[$firstFolder] = Join-Path $targetDir $firstFolder
    }
}

$archivePaths = @()
$archivePaths += $requiredRootFiles | ForEach-Object { Join-Path $targetDir $_ }
$archivePaths += $topLevelFolders.Values

Compress-Archive -Path $archivePaths -DestinationPath $zipFile -Force

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

# Clean up copied root files
foreach ($file in $requiredRootFiles) {
    $targetPath = Join-Path $targetDir $file
    if (Test-Path -LiteralPath $targetPath) {
        Remove-Item -LiteralPath $targetPath -Force
        Write-Host "  Removed root file: $file" -ForegroundColor Yellow
    }
}

# Clean up scripts folder
$scriptsTargetDir = Join-Path $targetDir "scripts"
if (Test-Path -LiteralPath $scriptsTargetDir) {
    Remove-Item -LiteralPath $scriptsTargetDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Removed scripts folder" -ForegroundColor Yellow
}

Write-Host "Done. Created: $zipFile"