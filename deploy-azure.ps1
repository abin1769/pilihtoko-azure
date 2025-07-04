# Azure Deployment Script untuk PilihToko App
Write-Host "=== Azure Deployment Script untuk PilihToko ===" -ForegroundColor Green

# Variables
$resourceGroupName = "rg-pilihtoko"
$appServicePlanName = "asp-pilihtoko"
$webAppName = "pilihtoko-app-$(Get-Random -Minimum 1000 -Maximum 9999)"
$location = "southeastasia"
$runtime = "PYTHON:3.11"

Write-Host "Resource Group: $resourceGroupName" -ForegroundColor Yellow
Write-Host "App Service Plan: $appServicePlanName" -ForegroundColor Yellow
Write-Host "Web App Name: $webAppName" -ForegroundColor Yellow

# Check Azure login
Write-Host "Checking Azure CLI configuration..." -ForegroundColor Yellow
$account = az account show --output json 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure first: az login" -ForegroundColor Red
    exit 1
}

# Configure Azure CLI to handle SSL issues
az config set core.use_cli_managed_oauth=false 2>$null
az config set extension.use_dynamic_install=yes_without_prompt 2>$null

Write-Host "Azure CLI configured successfully" -ForegroundColor Green

Write-Host "Creating Azure resources..." -ForegroundColor Blue

# Create Resource Group
az group create --name $resourceGroupName --location $location

# Create App Service Plan (Free tier)
az appservice plan create --name $appServicePlanName --resource-group $resourceGroupName --sku F1 --is-linux

# Create Web App with proper runtime
az webapp create --resource-group $resourceGroupName --plan $appServicePlanName --name $webAppName --runtime $runtime --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"

# Set environment variables
az webapp config appsettings set --resource-group $resourceGroupName --name $webAppName --settings FLASK_ENV=production SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Deploy code using zip deploy (recommended method)
Write-Host "Deploying application..." -ForegroundColor Blue

# Clean up old deployment files
Remove-Item "deployment.zip" -ErrorAction SilentlyContinue

# Create deployment zip with specific exclusions using a more efficient method
Write-Host "Creating deployment package..." -ForegroundColor Yellow

# First, create a temporary directory for clean deployment files
$tempDir = "temp_deploy"
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy files excluding problematic ones
$excludePatterns = @("deployment.zip", ".git", "__pycache__", "*.pyc", ".gitignore", "temp_deploy", "*.log")

Get-ChildItem -Path . -Recurse | Where-Object {
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($_.Name -like $pattern -or $_.FullName -like "*\.git\*" -or $_.FullName -like "*__pycache__*") {
            $exclude = $true
            break
        }
    }
    -not $exclude
} | ForEach-Object {
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
    $destPath = Join-Path $tempDir $relativePath
    $destDir = Split-Path $destPath -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    if (-not $_.PSIsContainer) {
        Copy-Item $_.FullName $destPath -Force
    }
}

# Create zip from temp directory
Compress-Archive -Path "$tempDir\*" -DestinationPath "deployment.zip" -CompressionLevel Fastest -Force

# Clean up temp directory
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Deployment package created successfully" -ForegroundColor Green

# Deploy using the newer az webapp deploy command with retry mechanism
$maxRetries = 3
$retryCount = 0
$deploySuccess = $false

while ($retryCount -lt $maxRetries -and -not $deploySuccess) {
    $retryCount++
    Write-Host "Deployment attempt $retryCount of $maxRetries..." -ForegroundColor Yellow
    
    try {
        az webapp deploy --resource-group $resourceGroupName --name $webAppName --src-path "deployment.zip" --type zip --async false
        if ($LASTEXITCODE -eq 0) {
            $deploySuccess = $true
            Write-Host "Deployment successful!" -ForegroundColor Green
        } else {
            Write-Host "Deployment attempt $retryCount failed" -ForegroundColor Red
            if ($retryCount -lt $maxRetries) {
                Write-Host "Waiting 30 seconds before retry..." -ForegroundColor Yellow
                Start-Sleep -Seconds 30
            }
        }
    }
    catch {
        Write-Host "Error during deployment: $($_.Exception.Message)" -ForegroundColor Red
        if ($retryCount -lt $maxRetries) {
            Write-Host "Waiting 30 seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds 30
        }
    }
}

if ($deploySuccess) {
    Write-Host "=== DEPLOYMENT SUCCESSFUL ===" -ForegroundColor Green
    Write-Host "Your app is available at: https://$webAppName.azurewebsites.net" -ForegroundColor Green
    
    # Wait a bit for the app to start
    Write-Host "Waiting for app to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Check app status
    Write-Host "Checking app status..." -ForegroundColor Yellow
    $appUrl = "https://$webAppName.azurewebsites.net"
    try {
        $response = Invoke-WebRequest -Uri $appUrl -TimeoutSec 30 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "App is running successfully!" -ForegroundColor Green
        } else {
            Write-Host "App responded with status code: $($response.StatusCode)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "App may still be starting. Check manually at: $appUrl" -ForegroundColor Yellow
    }
    
    Remove-Item "deployment.zip" -ErrorAction SilentlyContinue
} else {
    Write-Host "=== DEPLOYMENT FAILED AFTER $maxRetries ATTEMPTS ===" -ForegroundColor Red
    Write-Host "Please check the logs and try again" -ForegroundColor Red
    Remove-Item "deployment.zip" -ErrorAction SilentlyContinue
    exit 1
}
