##############################################################################
# Entretelas Theme Packaging Script (PowerShell)
# 
# This script creates an importable ZIP file for PrestaShop 9.1.x
# The ZIP structure follows PrestaShop's theme import requirements:
# - One top-level folder named "entretelas/"
# - Contains all theme runtime files (assets/, config/, templates/, etc.)
# - Excludes development artifacts and build files
##############################################################################

# Configuration
$ErrorActionPreference = "Stop"
$ThemeName = "entretelas"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ThemeSource = Join-Path $ProjectRoot "themes\$ThemeName"
$DistDir = Join-Path $ProjectRoot "dist"
$OutputZip = Join-Path $DistDir "$ThemeName.zip"
$TempDir = Join-Path $env:TEMP ("entretelas_package_" + (Get-Random))

# Cleanup function
function Cleanup {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
        Write-Host "Cleaned up temporary files" -ForegroundColor Green
    }
}

# Set cleanup on exit
trap { Cleanup }

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Entretelas Theme Packaging Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if theme source exists
if (-not (Test-Path $ThemeSource)) {
    Write-Host "ERROR: Theme source directory not found: $ThemeSource" -ForegroundColor Red
    exit 1
}

# Check if theme.yml exists
$ThemeYml = Join-Path $ThemeSource "config\theme.yml"
if (-not (Test-Path $ThemeYml)) {
    Write-Host "ERROR: theme.yml not found in $ThemeSource\config\" -ForegroundColor Red
    exit 1
}

# Verify theme name in theme.yml
$ThemeYmlContent = Get-Content $ThemeYml -Raw
if (-not ($ThemeYmlContent -match "name:\s+$ThemeName")) {
    Write-Host "WARNING: theme.yml does not contain 'name: $ThemeName'" -ForegroundColor Yellow
    Write-Host "Please verify the theme configuration." -ForegroundColor Yellow
}

Write-Host "✓ Theme source found: $ThemeSource" -ForegroundColor Green
Write-Host "✓ Theme configuration validated" -ForegroundColor Green
Write-Host ""

# Create dist directory if it doesn't exist
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

# Create temporary packaging directory
$PackageDir = Join-Path $TempDir $ThemeName
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null

Write-Host "Copying theme files..."

# Define exclusion patterns
$ExcludePatterns = @(
    '.git',
    '.github',
    '.idea',
    '.vscode',
    '.DS_Store',
    'Thumbs.db',
    'node_modules',
    '.sass-cache',
    'cache'
)

$ExcludeFilePatterns = @(
    '*.log',
    '*.swp',
    '*.swo',
    '*~'
)

# Copy theme files with exclusions
Get-ChildItem -Path $ThemeSource -Recurse | Where-Object {
    $item = $_
    $shouldExclude = $false
    
    # Check directory/file name exclusions
    foreach ($pattern in $ExcludePatterns) {
        if ($item.Name -eq $pattern -or $item.FullName -match [regex]::Escape($pattern)) {
            $shouldExclude = $true
            break
        }
    }
    
    # Check file pattern exclusions
    if (-not $shouldExclude -and -not $item.PSIsContainer) {
        foreach ($pattern in $ExcludeFilePatterns) {
            if ($item.Name -like $pattern) {
                $shouldExclude = $true
                break
            }
        }
    }
    
    -not $shouldExclude
} | ForEach-Object {
    $targetPath = $_.FullName.Replace($ThemeSource, $PackageDir)
    
    if ($_.PSIsContainer) {
        if (-not (Test-Path $targetPath)) {
            New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        }
    } else {
        $targetDir = Split-Path -Parent $targetPath
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        Copy-Item $_.FullName -Destination $targetPath -Force
    }
}

Write-Host "✓ Theme files copied to temporary directory" -ForegroundColor Green
Write-Host ""

# Verify critical files exist
Write-Host "Verifying theme structure..."

$CriticalFiles = @(
    "config\theme.yml",
    "preview.png"
)

foreach ($file in $CriticalFiles) {
    $filePath = Join-Path $PackageDir $file
    if (-not (Test-Path $filePath)) {
        Write-Host "ERROR: Critical file missing: $file" -ForegroundColor Red
        exit 1
    }
}

$CriticalDirs = @(
    "assets",
    "config",
    "templates"
)

foreach ($dir in $CriticalDirs) {
    $dirPath = Join-Path $PackageDir $dir
    if (-not (Test-Path $dirPath)) {
        Write-Host "ERROR: Critical directory missing: $dir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✓ Theme structure validated" -ForegroundColor Green
Write-Host ""

# Create ZIP file
Write-Host "Creating ZIP archive..."

# Remove existing ZIP if it exists
if (Test-Path $OutputZip) {
    Remove-Item $OutputZip -Force
}

# Create ZIP archive
# Use .NET compression to ensure proper ZIP structure
Add-Type -AssemblyName System.IO.Compression.FileSystem

# Compress from temp directory to ensure correct structure
[System.IO.Compression.ZipFile]::CreateFromDirectory($TempDir, $OutputZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)

Write-Host "✓ ZIP archive created" -ForegroundColor Green
Write-Host ""

# Get ZIP file size
$ZipSize = (Get-Item $OutputZip).Length
$ZipSizeFormatted = "{0:N2} MB" -f ($ZipSize / 1MB)

# Verify ZIP structure
Write-Host "Verifying ZIP structure..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($OutputZip)
$topLevelEntries = $zip.Entries | Where-Object { $_.FullName -match "^$ThemeName/" } | Select-Object -First 1
$zip.Dispose()

if ($topLevelEntries) {
    Write-Host "✓ ZIP structure is correct (contains $ThemeName/ as top-level folder)" -ForegroundColor Green
} else {
    Write-Host "ERROR: ZIP structure is incorrect" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "SUCCESS! Theme packaged successfully" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output: $OutputZip"
Write-Host "Size:   $ZipSizeFormatted"
Write-Host ""
Write-Host "Import Instructions:"
Write-Host "1. Go to PrestaShop Back Office"
Write-Host "2. Navigate to: Appearance → Theme & Logo"
Write-Host "3. Click: Add a theme"
Write-Host "4. Select: Import from computer"
Write-Host "5. Upload: $OutputZip"
Write-Host ""

# Cleanup
Cleanup
