# PilihToko - Aplikasi Pencarian Toko Sembako

Aplikasi web berbasis Flask untuk mencari toko sembako terdekat menggunakan algoritma Dijkstra dengan visualisasi interaktif.

## Fitur Utama

- **Rekomendasi Barang**: Mencari toko terbaik berdasarkan barang yang diinginkan
- **Toko Terdekat**: Menampilkan daftar toko berdasarkan jarak terdekat
- **Rute Spesifik**: Menampilkan rute dari rumah ke toko tertentu
- **Visualisasi Algoritma**: Melihat cara kerja algoritma Dijkstra step-by-step
- **Peta Interaktif**: Visualisasi jalur dan lokasi pada peta

## Teknologi

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Algoritma**: Dijkstra untuk pencarian jalur terpendek
- **Fuzzy Logic**: Sistem penilaian toko berdasarkan jarak, rating, dan stok

## Struktur Project

```
PilihToko/
├── app.py              # Aplikasi Flask utama
├── requirements.txt    # Dependencies Python
├── Procfile           # Konfigurasi deployment
├── runtime.txt        # Versi Python
├── data/              # Data JSON
│   ├── graf_jalan.json
│   ├── map.json
│   ├── rumah.json
│   └── toko.json
├── modules/           # Modul Python
│   ├── dijkstra_graf.py
│   ├── data_loader.py
│   ├── fuzzy.py
│   └── visual.py
├── static/            # File statis
│   ├── css/
│   ├── js/
│   └── img/
└── templates/         # Template HTML
```

## Instalasi Lokal

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd PilihToko-main
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**:
   ```bash
   python app.py
   ```

4. **Buka browser**: `http://localhost:8000`

## Deployment ke Azure

### Prasyarat
- Azure CLI
- Azure Account

### Deployment Otomatis
```powershell
.\deploy-azure.ps1
```

### Manual Deployment
Lihat [DEPLOYMENT.md](DEPLOYMENT.md) untuk panduan lengkap.

## Penggunaan

1. **Pilih Mode Pencarian**:
   - Rekomendasi berdasarkan barang
   - Toko terdekat dari rumah
   - Rute spesifik ke toko

2. **Pilih Rumah**: Tentukan titik awal pencarian

3. **Pilih Barang/Toko**: Sesuai mode yang dipilih

4. **Lihat Hasil**: Aplikasi akan menampilkan:
   - Rute optimal
   - Jarak tempuh
   - Visualisasi peta
   - Informasi toko

## Algoritma

- **Dijkstra**: Untuk mencari jalur terpendek
- **BFS**: Untuk visualisasi jalur pada grid
- **Fuzzy Logic**: Untuk sistem rekomendasi toko

## Kontributor

- Developer: [Your Name]
- Version: 1.0.0

## License

MIT License
