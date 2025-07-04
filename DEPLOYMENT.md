# Deploy PilihToko ke Azure App Service

## Prasyarat

1. **Azure CLI**: Install Azure CLI dari [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Account**: Pastikan Anda memiliki akun Azure yang aktif
3. **Git**: Untuk version control (opsional)

## Langkah Deployment

### Metode 1: Menggunakan PowerShell Script (Otomatis)

1. Buka PowerShell sebagai Administrator
2. Navigate ke folder project:
   ```powershell
   cd "C:\Users\abins\Downloads\PilihToko-main"
   ```

3. Login ke Azure:
   ```powershell
   az login
   ```

4. Jalankan deployment script:
   ```powershell
   .\deploy-azure.ps1
   ```

### Metode 2: Manual Deployment

1. **Login ke Azure**:
   ```bash
   az login
   ```

2. **Buat Resource Group**:
   ```bash
   az group create --name rg-pilihtoko --location "Southeast Asia"
   ```

3. **Buat App Service Plan**:
   ```bash
   az appservice plan create --name asp-pilihtoko --resource-group rg-pilihtoko --sku F1 --is-linux
   ```

4. **Buat Web App**:
   ```bash
   az webapp create --resource-group rg-pilihtoko --plan asp-pilihtoko --name pilihtoko-app-unique --runtime "PYTHON|3.11"
   ```

5. **Set Environment Variables**:
   ```bash
   az webapp config appsettings set --resource-group rg-pilihtoko --name pilihtoko-app-unique --settings FLASK_ENV=production PYTHONPATH=.
   ```

6. **Deploy Code**:
   ```bash
   az webapp deployment source config-zip --resource-group rg-pilihtoko --name pilihtoko-app-unique --src deployment.zip
   ```

### Metode 3: Deployment dari Git

1. **Setup Git deployment**:
   ```bash
   az webapp deployment source config --resource-group rg-pilihtoko --name pilihtoko-app-unique --repo-url https://github.com/yourusername/PilihToko.git --branch main --manual-integration
   ```

## Konfigurasi Environment Variables

Setelah deployment, Anda bisa mengatur environment variables tambahan:

```bash
az webapp config appsettings set --resource-group rg-pilihtoko --name your-app-name --settings \
    FLASK_ENV=production \
    PYTHONPATH=. \
    CUSTOM_SETTING=value
```

## Monitoring dan Troubleshooting

1. **Lihat logs aplikasi**:
   ```bash
   az webapp log tail --resource-group rg-pilihtoko --name your-app-name
   ```

2. **Download logs**:
   ```bash
   az webapp log download --resource-group rg-pilihtoko --name your-app-name
   ```

3. **Restart aplikasi**:
   ```bash
   az webapp restart --resource-group rg-pilihtoko --name your-app-name
   ```

## Scaling dan Performance

### Upgrade ke Plan Berbayar
```bash
az appservice plan update --name asp-pilihtoko --resource-group rg-pilihtoko --sku B1
```

### Auto-scaling (untuk plan yang mendukung)
```bash
az monitor autoscale create --resource-group rg-pilihtoko --resource your-app-name --resource-type Microsoft.Web/sites --name autoscale-settings --min-count 1 --max-count 3 --count 1
```

## Custom Domain dan SSL

1. **Tambah custom domain**:
   ```bash
   az webapp config hostname add --webapp-name your-app-name --resource-group rg-pilihtoko --hostname yourdomain.com
   ```

2. **Enable SSL**:
   ```bash
   az webapp config ssl bind --certificate-thumbprint thumbprint --ssl-type SNI --name your-app-name --resource-group rg-pilihtoko
   ```

## Cleanup Resources

Untuk menghapus semua resources yang dibuat:

```bash
az group delete --name rg-pilihtoko --yes --no-wait
```

## URLs Penting

- **Azure Portal**: [https://portal.azure.com](https://portal.azure.com)
- **App Service Documentation**: [https://docs.microsoft.com/en-us/azure/app-service/](https://docs.microsoft.com/en-us/azure/app-service/)
- **Azure CLI Reference**: [https://docs.microsoft.com/en-us/cli/azure/webapp](https://docs.microsoft.com/en-us/cli/azure/webapp)

## Troubleshooting Umum

1. **Application failed to start**:
   - Periksa `requirements.txt`
   - Periksa `Procfile` atau startup command
   - Lihat application logs

2. **Module not found**:
   - Pastikan semua dependencies ada di `requirements.txt`
   - Periksa `PYTHONPATH` environment variable

3. **Port binding issues**:
   - Pastikan aplikasi menggunakan `PORT` environment variable
   - Gunakan `0.0.0.0` sebagai host

4. **Static files tidak load**:
   - Pastikan path static files benar
   - Untuk production, pertimbangkan menggunakan CDN atau Azure Storage
