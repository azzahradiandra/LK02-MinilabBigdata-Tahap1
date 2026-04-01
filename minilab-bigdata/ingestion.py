import pandas as pd
from sqlalchemy import create_engine
import boto3
from io import BytesIO

# --- 1. SETTING KONEKSI ---
# Koneksi ke Postgres (RDBMS Sumber)
pg_url = 'postgresql://user_admin:password123@localhost:5432/db_sumber'
engine = create_engine(pg_url)

# Koneksi ke MinIO (Object Storage)
minio_client = boto3.client('s3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin_minio',
    aws_secret_access_key='password_minio',
    region_name='us-east-1'
)

# --- 2. PROSES AMBIL DATA DARI POSTGRES ---
print("Sedang mengambil data dari PostgreSQL...")
query = "SELECT * FROM penjualan" # Pastikan tabel 'penjualan' sudah kamu buat
df_pg = pd.read_sql(query, engine)

# --- 3. PROSES SIMPAN KE MINIO (INGESTION) ---
print("Sedang mengirim data ke MinIO...")
csv_buffer = BytesIO()
df_pg.to_csv(csv_buffer, index=False)

minio_client.put_object(
    Bucket='data-lake', 
    Key='raw/data_penjualan_rdbms.csv', 
    Body=csv_buffer.getvalue()
)

print("Proses Ingestion Selesai! Cek dashboard MinIO di localhost:9001")