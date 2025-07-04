# Script untuk membuat ZIP deployment
Write-Host "=== Membuat ZIP File untuk Deployment Manual ===" -ForegroundColor Green

# File dan folder yang perlu di-include
$includeFiles = @(
    "app.py",
    "requirements.txt", 
    "Procfile",
    "runtime.txt",
    "data",
    "modules", 
    "static",
    "templates"
)

# Hapus ZIP lama jika ada
if (Test-Path "pilihtoko-deployment.zip") {
    Remove-Item "pilihtoko-deployment.zip" -Force
    Write-Host "Menghapus ZIP file lama..." -ForegroundColor Yellow
}

Write-Host "Membuat ZIP file untuk deployment..." -ForegroundColor Blue

# Buat ZIP file dengan file yang diperlukan saja
$compress = @{
    Path = $includeFiles
    CompressionLevel = "Optimal"
    DestinationPath = "pilihtoko-deployment.zip"
}

try {
    Compress-Archive @compress
    Write-Host "✅ ZIP file berhasil dibuat: pilihtoko-deployment.zip" -ForegroundColor Green
    Write-Host "" 
    Write-Host "📁 File yang di-include:" -ForegroundColor Cyan
    foreach ($file in $includeFiles) {
        if (Test-Path $file) {
            Write-Host "   ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $file (tidak ditemukan)" -ForegroundColor Red
        }
    }
    Write-Host ""
    Write-Host "🚀 Langkah selanjutnya:" -ForegroundColor Yellow
    Write-Host "1. Buka https://portal.azure.com" 
    Write-Host "2. Buat Web App baru (Python 3.11, Linux)"
    Write-Host "3. Upload file 'pilihtoko-deployment.zip' via Deployment Center"
    Write-Host "4. Lihat panduan lengkap di DEPLOY-MANUAL.md"
    
} catch {
    Write-Host "❌ Error membuat ZIP file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
