# Script để tự động chuyển sang Node.js version phù hợp cho project này
# Chạy: .\use-node-version.ps1 hoặc powershell -ExecutionPolicy Bypass -File .\use-node-version.ps1

$requiredVersion = "22.21.0"
$nvmrcPath = Join-Path $PSScriptRoot ".nvmrc"

if (Test-Path $nvmrcPath) {
    $requiredVersion = Get-Content $nvmrcPath -Raw | ForEach-Object { $_.Trim() }
}

Write-Host "Checking for Node.js version $requiredVersion..." -ForegroundColor Cyan

# Kiểm tra xem version đã được cài chưa
$installedVersions = nvm list | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches.Value }

if ($installedVersions -contains $requiredVersion) {
    Write-Host "Switching to Node.js $requiredVersion..." -ForegroundColor Green
    nvm use $requiredVersion
    Write-Host "✅ Switched to Node.js $requiredVersion" -ForegroundColor Green
    Write-Host "Current Node.js version: $(node --version)" -ForegroundColor Yellow
} else {
    Write-Host "Node.js $requiredVersion not found. Installing..." -ForegroundColor Yellow
    nvm install $requiredVersion
    nvm use $requiredVersion
    Write-Host "✅ Installed and switched to Node.js $requiredVersion" -ForegroundColor Green
    Write-Host "Current Node.js version: $(node --version)" -ForegroundColor Yellow
}

