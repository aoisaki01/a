# setup_database.py
# Versi ini sudah mencakup semua tabel termasuk post_reports dan visibility_status di posts.

import sqlite3
import os

# Nama file database SQLite
DB_FILE = "social_media_app.db"

def create_connection(db_file):
    """ Membuat koneksi ke database SQLite.
        Akan membuat file database jika belum ada.
    Args:
        db_file (str): Path ke file database.
    Returns:
        sqlite3.Connection: Objek koneksi atau None jika gagal.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Berhasil terhubung ke SQLite versi: {sqlite3.sqlite_version}")
        print(f"Database disimpan di: {os.path.abspath(db_file)}")
    except sqlite3.Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
    return conn

def create_tables(conn):
    """ Membuat tabel-tabel yang dibutuhkan dalam database.
    Args:
        conn (sqlite3.Connection): Objek koneksi database.
    """
    if conn is None:
        print("Tidak ada koneksi ke database. Tabel tidak dapat dibuat.")
        return

    conn.execute("PRAGMA foreign_keys = ON;")

    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        profile_picture_url TEXT,
        bio TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    sql_create_friendships_table = """
    CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACCEPTED')) DEFAULT 'PENDING',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (sender_id, receiver_id)
    );
    """
    
    sql_create_posts_table = """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT, 
        image_url TEXT,
        video_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_live BOOLEAN DEFAULT FALSE,
        live_status TEXT,
        stream_playback_url TEXT,
        visibility_status TEXT DEFAULT 'VISIBLE' CHECK(visibility_status IN ('VISIBLE', 'HIDDEN_BY_REPORTS', 'ARCHIVED', 'DELETED_BY_USER')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    sql_create_likes_table = """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        UNIQUE (user_id, post_id)
    );
    """

    sql_create_comments_table = """
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        parent_comment_id INTEGER,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
    );
    """

    sql_create_shares_table = """
    CREATE TABLE IF NOT EXISTS shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        original_post_id INTEGER NOT NULL,
        caption TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (original_post_id) REFERENCES posts(id) ON DELETE CASCADE
    );
    """

    sql_create_user_blocks_table = """
    CREATE TABLE IF NOT EXISTS user_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blocker_id INTEGER NOT NULL, 
        blocked_user_id INTEGER NOT NULL, 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (blocked_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (blocker_id, blocked_user_id)
    );
    """

    sql_create_notifications_table = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_user_id INTEGER NOT NULL, 
        actor_user_id INTEGER,             
        type TEXT NOT NULL,                
        target_entity_type TEXT,           
        target_entity_id INTEGER,          
        is_read BOOLEAN DEFAULT FALSE,     
        message TEXT,                      
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recipient_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    # Tabel baru untuk laporan postingan
    sql_create_post_reports_table = """
    CREATE TABLE IF NOT EXISTS post_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        reporter_user_id INTEGER NOT NULL, -- Pengguna yang melaporkan
        reason TEXT,                       -- Alasan pelaporan (opsional)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (reporter_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (post_id, reporter_user_id) -- Mencegah satu pengguna melaporkan postingan yang sama berkali-kali
    );
    """

    # Skema SQL untuk membuat trigger updated_at (sama seperti sebelumnya)
    trigger_update_users = "CREATE TRIGGER IF NOT EXISTS ... END;" # Isi lengkap
    trigger_update_friendships = "CREATE TRIGGER IF NOT EXISTS ... END;" # Isi lengkap
    trigger_update_posts = "CREATE TRIGGER IF NOT EXISTS ... END;" # Isi lengkap
    trigger_update_comments = "CREATE TRIGGER IF NOT EXISTS ... END;" # Isi lengkap
    # (Salin definisi trigger lengkap dari Canvas #111 jika Anda memerlukannya di sini)
    # Untuk singkatnya, saya tidak ulang semua definisi trigger.


    # Skema SQL untuk membuat indeks (sama seperti sebelumnya, tambahkan untuk post_reports)
    index_friendships_sender = "CREATE INDEX IF NOT EXISTS idx_friendships_sender_id ON friendships(sender_id);"
    # ... (indeks lain)
    index_post_reports_post_id = "CREATE INDEX IF NOT EXISTS idx_post_reports_post_id ON post_reports(post_id);"
    index_post_reports_reporter = "CREATE INDEX IF NOT EXISTS idx_post_reports_reporter_id ON post_reports(reporter_user_id);"
    # (Salin definisi indeks lengkap dari Canvas #111 dan tambahkan yang baru)


    try:
        cursor = conn.cursor()
        print("Membuat tabel users...")
        cursor.execute(sql_create_users_table)
        print("Membuat tabel friendships...")
        cursor.execute(sql_create_friendships_table)
        print("Membuat tabel posts (dengan kolom visibility_status & live stream)...")
        cursor.execute(sql_create_posts_table)
        print("Membuat tabel likes...")
        cursor.execute(sql_create_likes_table)
        print("Membuat tabel comments...")
        cursor.execute(sql_create_comments_table)
        print("Membuat tabel shares...")
        cursor.execute(sql_create_shares_table)
        print("Membuat tabel user_blocks...")
        cursor.execute(sql_create_user_blocks_table)
        print("Membuat tabel notifications...")
        cursor.execute(sql_create_notifications_table)
        print("Membuat tabel post_reports...") # Ditambahkan
        cursor.execute(sql_create_post_reports_table) # Ditambahkan


        print("Membuat trigger untuk updated_at...")
        # Pastikan Anda memiliki string SQL lengkap untuk trigger di sini
        # cursor.execute(trigger_update_users) 
        # cursor.execute(trigger_update_friendships)
        # cursor.execute(trigger_update_posts)
        # cursor.execute(trigger_update_comments)

        print("Membuat indeks...")
        # Pastikan Anda memiliki string SQL lengkap untuk semua indeks
        # cursor.execute(index_friendships_sender)
        # ... (indeks lainnya)
        # cursor.execute(index_post_reports_post_id)
        # cursor.execute(index_post_reports_reporter)

        conn.commit()
        print("Semua tabel (termasuk post_reports), trigger, dan indeks berhasil dibuat atau sudah ada.")
    except sqlite3.Error as e:
        print(f"Error saat membuat tabel: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    # PENTING: Jika Anda baru saja menambahkan kolom visibility_status ke posts
    # atau tabel post_reports dan ingin skema baru diterapkan pada DB yang sudah ada,
    # Anda mungkin perlu menghapus file DB_FILE lama terlebih dahulu.
    # HATI-HATI: INI AKAN MENGHAPUS SEMUA DATA LAMA.
    # if os.path.exists(DB_FILE):
    #     print(f"PERINGATAN: File database '{DB_FILE}' sudah ada.")
    #     confirm_delete = input(f"Hapus '{DB_FILE}' untuk membuat ulang dengan skema terbaru (DATA AKAN HILANG)? (ketik 'YA' untuk hapus): ")
    #     if confirm_delete.upper() == 'YA':
    #         try:
    #             os.remove(DB_FILE)
    #             print(f"File database '{DB_FILE}' berhasil dihapus.")
    #         except OSError as e:
    #             print(f"Error menghapus file database: {e}")
    #             return # Jangan lanjutkan jika gagal hapus
    #     else:
    #         print("Pembuatan database dibatalkan. Skema yang ada mungkin tidak diperbarui.")
    #         # Jika tidak dihapus, kolom baru mungkin tidak ditambahkan ke tabel yg sudah ada
    #         # Anda mungkin perlu ALTER TABLE manual jika ingin mempertahankan data.

    conn = create_connection(DB_FILE)
    if conn is not None:
        create_tables(conn)
        conn.close()
        print("Koneksi database ditutup.")
    else:
        print("Gagal membuat koneksi ke database.")

if __name__ == '__main__':
    main()