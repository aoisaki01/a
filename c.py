# setup_database.py
# Versi ini mencakup semua tabel termasuk kolom untuk attachment di chat_messages,
# kolom visibility_status dan live_stream di posts.

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

    # Mengaktifkan foreign key constraints (penting untuk integritas data)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Skema SQL untuk membuat tabel-tabel
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
        content TEXT, -- Bisa NULL untuk live stream atau post hanya media
        image_url TEXT,
        video_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_live BOOLEAN DEFAULT FALSE,         -- Untuk fitur live stream
        live_status TEXT,                    -- 'PENDING', 'LIVE', 'ENDED' (NULL jika bukan live)
        stream_playback_url TEXT,            -- URL untuk menonton live stream
        visibility_status TEXT DEFAULT 'VISIBLE' CHECK(visibility_status IN ('VISIBLE', 'HIDDEN_BY_REPORTS', 'ARCHIVED', 'DELETED_BY_USER')), -- Untuk fitur report
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

    sql_create_post_reports_table = """
    CREATE TABLE IF NOT EXISTS post_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        reporter_user_id INTEGER NOT NULL,
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (reporter_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (post_id, reporter_user_id)
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

    sql_create_chat_rooms_table = """
    CREATE TABLE IF NOT EXISTS chat_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user1_id, user2_id),
        CHECK (user1_id < user2_id)
    );
    """

    sql_create_chat_messages_table = """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_room_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        message_content TEXT, -- Bisa NULL jika ada attachment
        attachment_url TEXT NULL,
        attachment_type TEXT NULL, -- 'image', 'video', 'file', dll.
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    # Definisi Trigger
    triggers_sql = [
        """CREATE TRIGGER IF NOT EXISTS update_users_updated_at
           AFTER UPDATE ON users FOR EACH ROW BEGIN
           UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;""",
        """CREATE TRIGGER IF NOT EXISTS update_friendships_updated_at
           AFTER UPDATE ON friendships FOR EACH ROW BEGIN
           UPDATE friendships SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;""",
        """CREATE TRIGGER IF NOT EXISTS update_posts_updated_at
           AFTER UPDATE ON posts FOR EACH ROW BEGIN
           UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;""",
        """CREATE TRIGGER IF NOT EXISTS update_comments_updated_at
           AFTER UPDATE ON comments FOR EACH ROW BEGIN
           UPDATE comments SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;""",
        """CREATE TRIGGER IF NOT EXISTS update_chat_room_last_message_at
           AFTER INSERT ON chat_messages FOR EACH ROW BEGIN
           UPDATE chat_rooms SET last_message_at = NEW.created_at WHERE id = NEW.chat_room_id; END;"""
    ]

    # Definisi Indeks
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_friendships_sender_id ON friendships(sender_id);",
        "CREATE INDEX IF NOT EXISTS idx_friendships_receiver_id ON friendships(receiver_id);",
        "CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_posts_visibility_status ON posts(visibility_status, created_at DESC);", # Indeks untuk filter visibility
        "CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);",
        "CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);", # Tambahan
        "CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);",
        "CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);", # Tambahan
        "CREATE INDEX IF NOT EXISTS idx_shares_original_post_id ON shares(original_post_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_blocks_blocker_id ON user_blocks(blocker_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_blocks_blocked_user_id ON user_blocks(blocked_user_id);",
        "CREATE INDEX IF NOT EXISTS idx_post_reports_post_id ON post_reports(post_id);",
        "CREATE INDEX IF NOT EXISTS idx_post_reports_reporter_id ON post_reports(reporter_user_id);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_recipient_id ON notifications(recipient_user_id, is_read, created_at DESC);", # Diurutkan DESC untuk created_at
        "CREATE INDEX IF NOT EXISTS idx_notifications_actor_id ON notifications(actor_user_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_rooms_users ON chat_rooms(user1_id, user2_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_rooms_last_message ON chat_rooms(last_message_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_room_time ON chat_messages(chat_room_id, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_sender_id ON chat_messages(sender_id);"
    ]

    try:
        cursor = conn.cursor()
        
        tables_to_create = [
            ("users", sql_create_users_table), 
            ("friendships", sql_create_friendships_table),
            ("posts", sql_create_posts_table), 
            ("likes", sql_create_likes_table),
            ("comments", sql_create_comments_table), 
            ("shares", sql_create_shares_table),
            ("user_blocks", sql_create_user_blocks_table), 
            ("post_reports", sql_create_post_reports_table),
            ("notifications", sql_create_notifications_table), 
            ("chat_rooms", sql_create_chat_rooms_table),
            ("chat_messages", sql_create_chat_messages_table)
        ]

        for name, sql in tables_to_create:
            print(f"Membuat tabel {name}...")
            cursor.execute(sql)
        
        print("Membuat trigger...")
        for sql in triggers_sql: 
            cursor.execute(sql)

        print("Membuat indeks...")
        for sql in indexes_sql: 
            cursor.execute(sql)

        conn.commit()
        print("Semua tabel, trigger, dan indeks berhasil dibuat atau sudah ada.")
    except sqlite3.Error as e:
        print(f"Error saat membuat/memperbarui database: {e}")
    finally:
        if cursor: 
            cursor.close()

def main():
    # PENTING: Untuk menerapkan perubahan skema pada tabel yang sudah ada,
    # Anda mungkin perlu menghapus file DB lama terlebih dahulu.
    # HATI-HATI: INI AKAN MENGHAPUS SEMUA DATA LAMA.
    # Uncomment baris di bawah ini jika Anda ingin skrip ini menghapus DB lama
    # sebelum membuat yang baru (berguna saat development atau jika skema berubah drastis).
    
    # if os.path.exists(DB_FILE):
    #     print(f"PERINGATAN: File database '{DB_FILE}' sudah ada.")
    #     confirm_delete = input(f"Hapus '{DB_FILE}' untuk membuat ulang dengan skema terbaru (SEMUA DATA AKAN HILANG)? (ketik 'YA' untuk hapus): ")
    #     if confirm_delete.upper() == 'YA':
    #         try:
    #             os.remove(DB_FILE)
    #             print(f"File database '{DB_FILE}' berhasil dihapus.")
    #         except OSError as e:
    #             print(f"Error menghapus file database: {e}")
    #             return # Jangan lanjutkan jika gagal hapus
    #     else:
    #         print("Pembuatan/pembaruan database dibatalkan oleh pengguna.")
    #         return

    conn = create_connection(DB_FILE)
    if conn is not None:
        create_tables(conn)
        conn.close()
        print("Koneksi database ditutup.")
    else:
        print("Gagal membuat koneksi ke database.")

if __name__ == '__main__':
    main()
