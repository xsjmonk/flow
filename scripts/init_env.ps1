$ErrorActionPreference = "Stop"

Write-Host "Running init script: $PSCommandPath"

$scriptDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $scriptDir
$environmentFile = Join-Path $repoRoot "environment.yml"
$launchDirectory = (Get-Location).Path

function Initialize-CondaSession {
    $condaCommand = Get-Command conda -ErrorAction SilentlyContinue
    if (-not $condaCommand) {
        throw "Conda is not available on PATH."
    }

    $hookScript = & conda shell.powershell hook
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to initialize Conda shell integration."
    }

    Invoke-Expression ($hookScript -join [Environment]::NewLine)
}

function Get-CondaEnvironmentName {
    param([string]$EnvironmentYamlPath)

    $yaml = Get-Content -LiteralPath $EnvironmentYamlPath -Raw -Encoding UTF8
    $match = [regex]::Match($yaml, '(?m)^\s*name\s*:\s*(?<name>[^\r\n#]+?)\s*$')
    if (-not $match.Success) {
        throw "Unable to determine Conda environment name from $EnvironmentYamlPath"
    }

    return $match.Groups["name"].Value.Trim()
}

function Test-CondaEnvExists {
    param([string]$EnvironmentName)
    $out = & conda env list 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $false }
    return ($out | Select-String -Pattern ("^" + [regex]::Escape($EnvironmentName) + "\s")) -ne $null
}

function Ensure-CondaEnvironment {
    param([string]$EnvironmentName, [string]$EnvironmentYamlPath)

    if (-not (Test-CondaEnvExists -EnvironmentName $EnvironmentName)) {
        Write-Host "Creating Conda environment: $EnvironmentName"
        & conda env create -f $EnvironmentYamlPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create Conda environment: $EnvironmentName"
        }
    }
    else {
        Write-Host "Conda environment already exists: $EnvironmentName"
    }

    if ($env:CONDA_DEFAULT_ENV -ne $EnvironmentName) {
        Write-Host "Activating Conda environment: $EnvironmentName"
        conda activate $EnvironmentName
    }
    else {
        Write-Host "Conda environment already active: $EnvironmentName"
    }
}

function Repair-CondaEnvironment {
    param([string]$EnvironmentName, [string]$EnvironmentYamlPath)

    Write-Host "Repairing Conda environment using environment.yml..."

    $repairOutput = & conda env update -n $EnvironmentName -f $EnvironmentYamlPath 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        $errorDetails = if ($repairOutput) { $repairOutput } else { "Unknown error" }
        throw "Failed to update Conda environment.`n`nDetails:`n$errorDetails"
    }

    Write-Host "Environment repaired successfully." -ForegroundColor Green
}

function Get-CondaEnvironmentPackages {
    param([string]$EnvironmentName)

    $out = & conda list -n $EnvironmentName 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $out) {
        throw "Failed to list packages in Conda environment: $EnvironmentName"
    }

    $packages = @{}
    foreach ($line in $out) {
        if ($line -match '^#') { continue }
        if ($line -match '^\s*$') { continue }

        $parts = $line -split '(?>\s+)', 2
        if ($parts.Count -ge 2) {
            $packages[$parts[0].Trim()] = $parts[1].Trim()
        }
    }

    return $packages
}

function Get-EnvironmentYamlPackages {
    param([string]$EnvironmentYamlPath)

    $yaml = Get-Content -LiteralPath $EnvironmentYamlPath -Raw -Encoding UTF8

    $packages = @{}

    $lines = $yaml -split '(?>\r\n|\r|\n)'
    $inDependencies = $false

    foreach ($line in $lines) {
        if ($line -match '^\s*dependencies\s*:') {
            $inDependencies = $true
            continue
        }

        if ($inDependencies) {
            if ($line -match '^\s*[a-z]') {
                break
            }

            if ($line -match '^\s*-\s*(.+)') {
                $pkg = $matches[1].Trim()
                if ($pkg) {
                    $packages[$pkg] = $pkg
                }
            }
        }
    }

    return $packages
}

function Show-PackageStates {
    param(
        [hashtable]$RequiredPackages,
        [hashtable]$InstalledPackages
    )

    $maxNameLen = 20
    foreach ($pkg in $RequiredPackages.Keys) {
        $normalizedName = $pkg -replace '=.*$', ''
        if ($normalizedName.Length -gt $maxNameLen) { $maxNameLen = $normalizedName.Length }
    }
    if ($maxNameLen -gt 40) { $maxNameLen = 40 }

    Write-Host ""
    Write-Host "Package Status:"
    Write-Host ("-" * ($maxNameLen + 30))

    foreach ($pkg in $RequiredPackages.Keys) {
        $normalizedName = $pkg -replace '=.*$', ''
        $installedVersion = $InstalledPackages[$normalizedName]
        if ($installedVersion) {
            $displayName = if ($normalizedName.Length -gt $maxNameLen) { $normalizedName.Substring(0, $maxNameLen - 3) + "..." } else { $normalizedName }
            Write-Host ("  {0,-$maxNameLen}  [INSTALLED] {1}" -f $displayName, $installedVersion)
        }
        else {
            $displayName = if ($normalizedName.Length -gt $maxNameLen) { $normalizedName.Substring(0, $maxNameLen - 3) + "..." } else { $normalizedName }
            Write-Host ("  {0,-$maxNameLen}  [MISSING]" -f $displayName) -ForegroundColor Yellow
        }
    }

    Write-Host ("-" * ($maxNameLen + 30))
}

$condaEnvironmentName = Get-CondaEnvironmentName -EnvironmentYamlPath $environmentFile

Write-Host "Initializing Conda environment: $condaEnvironmentName"

try {
    Initialize-CondaSession
    Ensure-CondaEnvironment -EnvironmentName $condaEnvironmentName -EnvironmentYamlPath $environmentFile

    Repair-CondaEnvironment -EnvironmentName $condaEnvironmentName -EnvironmentYamlPath $environmentFile

    Write-Host "Fetching package lists..."
    $installedPackages = Get-CondaEnvironmentPackages -EnvironmentName $condaEnvironmentName
    $requiredPackages = Get-EnvironmentYamlPackages -EnvironmentYamlPath $environmentFile

    Show-PackageStates -RequiredPackages $requiredPackages -InstalledPackages $installedPackages

    Write-Host ""
    Write-Host "Conda environment initialization complete." -ForegroundColor Green
}
finally {
    # no-op
}