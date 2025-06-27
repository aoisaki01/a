# File: add_visibility_status_column.py
import sqlite3
import os

DB_FILE = "social_media_app.db" # Pastikan nama file database Anda benar

def add_column_if_not_exists():
    conn = None
    try:
        db_path = os.path.join(os.getcwd(), DB_FILE) # Menggunakan path absolut
        if not os.path.exists(db_path):
            print(f"Error: File database '{DB_FILE}' tidak ditemukan di '{db_path}'.")
            print("Pastikan Anda menjalankan skrip ini di direktori yang sama dengan file database Anda,")
            print("atau jalankan setup_database.py terlebih dahulu jika ini database baru.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Terhubung ke database: {os.path.abspath(DB_FILE)}")

        # Cek apakah kolom visibility_status sudah ada
        cursor.execute("PRAGMA table_info(posts);")
        columns = [info[1] for info in cursor.fetchall()]

        if 'visibility_status' not in columns:
            print("Menambahkan kolom 'visibility_status' ke tabel 'posts'...")
            cursor.execute("ALTER TABLE posts ADD COLUMN visibility_status TEXT DEFAULT 'VISIBLE';")
            conn.commit()
            print("Kolom 'visibility_status' berhasil ditambahkan dengan nilai default 'VISIBLE'.")
        else:
            print("Kolom 'visibility_status' sudah ada di tabel 'posts'. Tidak ada perubahan dilakukan.")

    except sqlite3.Error as e:
        print(f"Error SQLite saat mencoba mengubah tabel 'posts': {e}")
    except Exception as e:
        print(f"Terjadi error umum: {e}")
    finally:
        if conn:
            conn.close()
            print("Koneksi database ditutup.")

if __name__ == '__main__':
    add_column_if_not_exists()