# LK02-MinilabBigdata-Tahap1

Repositori ini berisi dokumentasi dan implementasi **Minilab Ekosistem Big Data** untuk memenuhi Assignment Tahap 1. Fokus utama proyek ini adalah *deployment* infrastruktur menggunakan Docker dan proses *ingestion* data dari RDBMS ke Object Storage.

## 🛠️ Komponen & Toolstack
* **Infrastructure:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS)
* **RDBMS (Source):** PostgreSQL 15
* **Object Storage (Target):** MinIO (S3 Compatible)
* **Ingestion Engine:** Python 3.14 (Pandas, SQLAlchemy, Boto3)
* **Database Management:** DBeaver
* **Text Editor:** Sublime Text

---

## 📂 Struktur Proyek
```text
minilab-bigdata/
├── docker-compose.yml    # Konfigurasi PostgreSQL & MinIO
├── ingestion.py          # Script Python untuk Ingestion
├── data_tambahan.csv     # Contoh data tabular lokal
└── README.md             # Dokumentasi proyek

---

## 🏗️ 1. Deployment Infrastruktur
Buat file bernama `docker-compose.yml` di folder proyek Anda dan tempelkan kode berikut:

```yaml
version: '3.8'
services:
  # RDBMS Sumber (PostgreSQL)
  postgres-source:
    image: postgres:15
    container_name: postgres_source
    environment:
      POSTGRES_USER: user_admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: db_sumber
    ports:
      - "5432:5432"

  # Object Storage (MinIO)
  minio:
    image: minio/minio
    container_name: minio_storage
    ports:
      - "9000:9000" # API Port
      - "9001:9001" # Console Port
    environment:
      MINIO_ROOT_USER: admin_minio
      MINIO_ROOT_PASSWORD: password_minio
    command: server /data --console-address ":9001"

Jalankan infrastruktur melalui Terminal:

Bash
docker-compose up -d

2. Inisialisasi Data Sumber (PostgreSQL)
Setelah container berjalan, buat tabel sumber melalui Terminal dengan perintah berikut:

Bash
docker exec -it postgres_source psql -U user_admin -d db_sumber -c "
CREATE TABLE penjualan (
    id SERIAL PRIMARY KEY,
    produk VARCHAR(100),
    jumlah INT,
    tanggal DATE
);
INSERT INTO penjualan (produk, jumlah, tanggal) VALUES 
('Laptop MacBook', 5, '2026-03-01'), 
('Mouse Wireless', 20, '2026-03-02'),
('Keyboard Mechanical', 10, '2026-03-03');"

3. Script Ingestion (Python)
Instal library pendukung di Terminal Mac Anda:

Bash
pip3 install pandas sqlalchemy psycopg2-binary boto3
Buat file bernama ingestion.py di Sublime Text dan tempelkan kode berikut:

Python
import pandas as pd
from sqlalchemy import create_engine
import boto3
from io import BytesIO

# 1. Konfigurasi Koneksi
pg_engine = create_engine('postgresql://user_admin:password123@localhost:5432/db_sumber')
minio_client = boto3.client('s3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin_minio',
    aws_secret_access_key='password_minio',
    region_name='us-east-1'
)

# 2. Proses Ingestion dari PostgreSQL
print("Sedang mengambil data dari PostgreSQL...")
try:
    df_pg = pd.read_sql("SELECT * FROM penjualan", pg_engine)
    
    # Simpan ke memori sebagai CSV
    csv_buffer = BytesIO()
    df_pg.to_csv(csv_buffer, index=False)
    
    # 3. Upload ke MinIO (Pastikan Bucket 'data-lake' sudah dibuat di localhost:9001)
    print("Sedang mengirim data ke MinIO...")
    minio_client.put_object(
        Bucket='data-lake', 
        Key='raw/data_penjualan_rdbms.csv', 
        Body=csv_buffer.getvalue()
    )
    print("Proses Ingestion Selesai!")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
Jalankan script melalui Terminal:

Bash
python3 ingestion.py

4. Feedback
Docker Volume: Jika terjadi kesalahan password, gunakan docker-compose down -v untuk membersihkan data volume lama.

Bucket MinIO: Pastikan login ke localhost:9001 dan membuat bucket bernama data-lake secara manual sebelum menjalankan script.

Analisis: Penggunaan Docker mempermudah isolasi environment, sementara Python Boto3 sangat fleksibel untuk menangani transmisi data ke Object Storage.
