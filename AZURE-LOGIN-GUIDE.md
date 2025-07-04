# Panduan Login Azure di VS Code

## Method 1: Login via Command Palette

1. **Buka Command Palette**:
   ```
   Ctrl + Shift + P (Windows/Linux)
   Cmd + Shift + P (Mac)
   ```

2. **Ketik dan pilih**:
   ```
   Azure: Sign In
   ```

3. **Ikuti instruksi**:
   - Browser akan terbuka otomatis
   - Login dengan akun Microsoft/Azure Anda
   - Kembali ke VS Code setelah berhasil

## Method 2: Login via Azure Extension Panel

1. **Buka Azure Panel**:
   - Klik icon Azure di sidebar kiri (🔷)
   - Atau tekan `Ctrl + Shift + A`

2. **Klik "Sign in to Azure"**:
   - Tombol biru akan muncul jika belum login
   - Klik untuk memulai proses login

3. **Complete authentication**:
   - Browser terbuka → Login → Kembali ke VS Code

## Method 3: Device Code Login (Alternatif)

Jika browser tidak bisa terbuka atau ada masalah:

1. **Command Palette** → `Azure: Sign In with Device Code`

2. **Copy device code** yang muncul di VS Code

3. **Buka browser manual** ke: https://microsoft.com/devicelogin

4. **Paste device code** dan login

## Troubleshooting

### Jika Login Gagal:

1. **Clear Azure cache**:
   - Command Palette → `Azure: Clear Local Cache`

2. **Logout dulu**:
   - Command Palette → `Azure: Sign Out`
   - Lalu coba login lagi

3. **Restart VS Code**:
   - Tutup VS Code → Buka lagi → Coba login

### Jika Extension tidak ada:

1. **Install Azure Account Extension**:
   - Go to Extensions (Ctrl+Shift+X)
   - Search: "Azure Account"
   - Install dari Microsoft

2. **Install Azure App Service Extension**:
   - Search: "Azure App Service"
   - Install dari Microsoft

## Verifikasi Login Berhasil

Setelah login berhasil, Anda akan melihat:

1. **Di Azure Panel**:
   - Nama akun Anda muncul
   - List subscription Azure
   - Resource groups (jika ada)

2. **Di Status Bar** (bawah VS Code):
   - Icon Azure dengan nama akun

3. **Test dengan Command**:
   - Command Palette → `Azure: Select Subscriptions`
   - Harus muncul list subscription Anda

## Setelah Login Berhasil

Anda bisa:
- Deploy aplikasi via VS Code
- Manage Azure resources
- Create new App Services
- Monitor aplikasi
