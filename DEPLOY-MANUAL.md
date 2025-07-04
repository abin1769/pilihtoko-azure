# Deploy Manual ke Azure App Service

## Cara 1: Deploy via Azure Portal (Paling Mudah)

### Langkah 1: Buat ZIP File
1. Pilih semua file dalam folder `PilihToko-main` (kecuali `.venv` dan `__pycache__`)
2. Klik kanan → "Send to" → "Compressed (zipped) folder"
3. Nama file: `pilihtoko-app.zip`

### Langkah 2: Login ke Azure Portal
1. Buka https://portal.azure.com
2. Login dengan akun Microsoft/Azure Anda
3. Jika belum punya akun, daftar gratis di https://azure.microsoft.com/free

### Langkah 3: Buat App Service
1. Klik "Create a resource" (+ icon)
2. Search "Web App" → pilih "Web App"
3. Klik "Create"

### Langkah 4: Konfigurasi Web App
```
Resource Group: Buat baru → "rg-pilihtoko"
Name: "pilihtoko-app-[angka-random]" (harus unik)
Publish: Code
Runtime stack: Python 3.11
Operating System: Linux
Region: Southeast Asia
App Service Plan: Buat baru (Free F1)
```

### Langkah 5: Deploy Code
1. Setelah Web App dibuat, buka resource tersebut
2. Di sidebar kiri, pilih "Deployment Center"
3. Pilih "ZIP Deploy"
4. Upload file `pilihtoko-app.zip` yang sudah dibuat
5. Klik "Deploy"

### Langkah 6: Set Environment Variables
1. Di sidebar kiri, pilih "Configuration"
2. Klik "Application settings"
3. Tambahkan:
   - Name: `FLASK_ENV`, Value: `production`
   - Name: `SCM_DO_BUILD_DURING_DEPLOYMENT`, Value: `true`
4. Klik "Save"

### Langkah 7: Restart App
1. Di sidebar kiri, pilih "Overview"
2. Klik "Restart"
3. Tunggu beberapa menit
4. Klik URL yang tertera untuk mengakses aplikasi

---

## Cara 2: Deploy via VS Code (Dengan Extension)

### Langkah 1: Install Extension
1. Buka VS Code
2. Install extension "Azure App Service"
3. Login ke Azure account dari VS Code

### Langkah 2: Deploy
1. Right-click pada folder project
2. Pilih "Deploy to Web App..."
3. Ikuti wizard yang muncul

---

## Cara 3: Deploy via GitHub (CI/CD)

### Langkah 1: Upload ke GitHub
1. Buat repository baru di GitHub
2. Upload semua file project

### Langkah 2: Setup GitHub Actions
1. Di Azure Portal, buka Web App yang sudah dibuat
2. Pilih "Deployment Center"
3. Pilih "GitHub"
4. Authorize dan pilih repository
5. Azure akan otomatis setup CI/CD

---

## Troubleshooting

### Jika aplikasi tidak jalan:
1. Buka "Log stream" di Azure Portal
2. Lihat error messages
3. Pastikan semua dependencies ada di `requirements.txt`

### Jika ada error startup:
1. Cek "Configuration" → "General settings"
2. Startup Command: `gunicorn app:app`
3. Restart aplikasi

### File yang perlu ada dalam ZIP:
- `app.py`
- `requirements.txt`
- `Procfile`
- `runtime.txt`
- Folder `data/`, `modules/`, `static/`, `templates/`

### File yang TIDAK perlu di ZIP:
- `.venv/`
- `__pycache__/`
- `.git/`
- `deployment.zip`
- `.env` (jika ada)
