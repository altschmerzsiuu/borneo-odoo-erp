# Borneo Berkuda Stable ERP (borneo-odoo-erp)

Sistem Informasi Manajemen & ERP Terpadu untuk **Borneo Berkuda Stable (BBS)** berbasis **Odoo 17 Community Edition** dan Docker.

---

## 📌 Modul Kustom (Custom Addons)

### 1. `bbs_operational` (Operasional & Kas BBS)
* **RAB Bulanan**: Pengajuan dan persetujuan Rencana Anggaran Biaya (RAB) per periode bulan/tahun.
* **Kas Operasional Harian**: Pencatatan arus kas operasional (uang masuk & keluar), biaya transfer otomatis Admin BCA, lampiran bukti transfer, dan alokasi ke dokumen RAB.
* **Integrasi Native Odoo Dashboards**: Scorecard KPI (Kas Masuk, Keluar, Saldo Kas Berjalan, Anggaran RAB), grafik pengeluaran per pos kategori (Bar Chart), pie chart distribusi per PIC, serta tabel transaksi kas terkini langsung di aplikasi bawaan **Dashboards** (`spreadsheet_dashboard`).
* **Laporan PDF**: Template cetak dokumen RAB & rincian realisasi kas operasional resmi berlogo BBS.

### 2. `bbs_stable` (Stable & Horse Management)
* **Data Kuda**: Profil kuda, silsilah/pedigree, foto, ras, status kepemilikan, dan riwayat kesehatan.
* **Pelatihan & Aktivitas**: Monitoring jadwal latihan harian/mingguan dan perawatan kandang.

---

## 🌳 Git Branching Strategy
* **`main`**: Branch produksi (Production). Kode yang sudah dites dan siap tayang di server VPS live.
* **`staging`**: Branch pengujian (Staging / Testing). Digunakan untuk mencoba fitur baru sebelum di-merge ke branch `main`.

---

## 🚀 Panduan Menjalankan di Server VPS (Sumopod)

### 1. Prasyarat di VPS
Pastikan VPS Anda (Ubuntu / Debian) sudah terinstal Docker dan Git:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git docker.io docker-compose-v2
sudo systemctl enable --now docker
```

### 2. Clone Repositori
```bash
# Buat direktori aplikasi
sudo mkdir -p /opt/borneoberkuda_odoo
sudo chown -R $USER:$USER /opt/borneoberkuda_odoo

# Clone repository
git clone https://github.com/altschmerzsiuu/borneo-odoo-erp.git /opt/borneoberkuda_odoo
cd /opt/borneoberkuda_odoo
```

### 3. Jalankan Docker Compose
```bash
# Menjalankan kontainer Odoo & PostgreSQL di background
docker compose up -d
```

### 4. Periksa Status Kontainer & Log
```bash
docker compose ps
docker compose logs -f web
```

### 5. Cara Upgrade Modul Setelah Update Kode
Setiap kali ada pembaruan kode dari GitHub:
```bash
cd /opt/borneoberkuda_odoo
git pull origin main
docker compose exec -T web odoo -c /etc/odoo/odoo.conf -d bbs_dev -u bbs_operational,bbs_stable --stop-after-init
docker compose restart web
```

---

## 💻 Panduan Menjalankan di Komputer Lokal (Windows)

1. Jalankan `start_dev.bat` untuk menyalakan kontainer Docker.
2. Akses Odoo di peramban (browser): `http://localhost:8069`.
3. Jalankan `stop_dev.bat` jika ingin mematikan kontainer.
