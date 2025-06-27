# setup_database.py
# (Tambahkan definisi tabel baru dan eksekusinya)

import sqlite3
import os

DB_FILE = "social_media_app.db"

def create_connection(db_file):
    # ... (fungsi create_connection sama seperti sebelumnya) ...
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Berhasil terhubung ke SQLite versi: {sqlite3.sqlite_version}")
        print(f"Database disimpan di: {os.path.abspath(db_file)}")
    except sqlite3.Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
    return conn

def create_tables(conn):
    if conn is None:
        print("Tidak ada koneksi ke database. Tabel tidak dapat dibuat.")
        return
    conn.execute("PRAGMA foreign_keys = ON;")

    # ... (SQL CREATE TABLE untuk users, friendships, posts, likes, comments, shares, user_blocks, post_reports, notifications tetap sama) ...
    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, full_name TEXT, profile_picture_url TEXT, bio TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );"""
    sql_create_friendships_table = """
    CREATE TABLE IF NOT EXISTS friendships (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACCEPTED')) DEFAULT 'PENDING',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (sender_id, receiver_id)
    );"""
    sql_create_posts_table = """
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT, image_url TEXT, video_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_live BOOLEAN DEFAULT FALSE, live_status TEXT, stream_playback_url TEXT,
        visibility_status TEXT DEFAULT 'VISIBLE' CHECK(visibility_status IN ('VISIBLE', 'HIDDEN_BY_REPORTS', 'ARCHIVED', 'DELETED_BY_USER')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );"""
    sql_create_likes_table = """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, post_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        UNIQUE (user_id, post_id)
    );"""
    sql_create_comments_table = """
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, post_id INTEGER NOT NULL,
        parent_comment_id INTEGER, content TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
    );"""
    sql_create_shares_table = """
    CREATE TABLE IF NOT EXISTS shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, original_post_id INTEGER NOT NULL,
        caption TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (original_post_id) REFERENCES posts(id) ON DELETE CASCADE
    );"""
    sql_create_user_blocks_table = """
    CREATE TABLE IF NOT EXISTS user_blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, blocker_id INTEGER NOT NULL, blocked_user_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (blocked_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (blocker_id, blocked_user_id)
    );"""
    sql_create_post_reports_table = """
    CREATE TABLE IF NOT EXISTS post_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER NOT NULL, reporter_user_id INTEGER NOT NULL,
        reason TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (reporter_user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (post_id, reporter_user_id)
    );"""
    sql_create_notifications_table = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, recipient_user_id INTEGER NOT NULL, actor_user_id INTEGER,
        type TEXT NOT NULL, target_entity_type TEXT, target_entity_id INTEGER,
        is_read BOOLEAN DEFAULT FALSE, message TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recipient_user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE CASCADE
    );"""

    # highlight-start
    # Tabel untuk Ruang Chat (Percakapan 1-on-1)
    sql_create_chat_rooms_table = """
    CREATE TABLE IF NOT EXISTS chat_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        -- Untuk memastikan keunikan dan query yang mudah untuk pasangan,
        -- user1_id akan selalu ID pengguna yang lebih kecil, user2_id yang lebih besar.
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- Diupdate saat ada pesan baru
        FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user1_id, user2_id),
        CHECK (user1_id < user2_id) -- Memastikan urutan ID
    );
    """

    # Tabel untuk Pesan Chat
    sql_create_chat_messages_table = """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_room_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        -- receiver_id secara implisit adalah pengguna lain di chat_room untuk 1-on-1
        message_content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        -- is_read bisa lebih kompleks, misal tabel terpisah untuk read receipts per user per pesan
        -- Untuk kesederhanaan, kita bisa tambahkan di sini, atau di-handle di client/notifikasi
        FOREIGN KEY (chat_room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    # highlight-end

    # ... (definisi trigger tetap sama) ...
    trigger_update_users = "CREATE TRIGGER IF NOT EXISTS update_users_updated_at AFTER UPDATE ON users FOR EACH ROW BEGIN UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;"
    trigger_update_friendships = "CREATE TRIGGER IF NOT EXISTS update_friendships_updated_at AFTER UPDATE ON friendships FOR EACH ROW BEGIN UPDATE friendships SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;"
    trigger_update_posts = "CREATE TRIGGER IF NOT EXISTS update_posts_updated_at AFTER UPDATE ON posts FOR EACH ROW BEGIN UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;"
    trigger_update_comments = "CREATE TRIGGER IF NOT EXISTS update_comments_updated_at AFTER UPDATE ON comments FOR EACH ROW BEGIN UPDATE comments SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id; END;"
    # highlight-start
    # Trigger untuk mengupdate last_message_at di chat_rooms saat ada pesan baru
    trigger_update_chat_room_last_message_at = """
    CREATE TRIGGER IF NOT EXISTS update_chat_room_last_message_at
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    BEGIN
        UPDATE chat_rooms
        SET last_message_at = NEW.created_at
        WHERE id = NEW.chat_room_id;
    END;
    """
    # highlight-end

    # Tambahkan indeks untuk tabel baru
    # highlight-start
    index_chat_rooms_users = "CREATE INDEX IF NOT EXISTS idx_chat_rooms_users ON chat_rooms(user1_id, user2_id);"
    index_chat_rooms_last_message = "CREATE INDEX IF NOT EXISTS idx_chat_rooms_last_message ON chat_rooms(last_message_at DESC);"
    index_chat_messages_room_time = "CREATE INDEX IF NOT EXISTS idx_chat_messages_room_time ON chat_messages(chat_room_id, created_at DESC);"
    index_chat_messages_sender = "CREATE INDEX IF NOT EXISTS idx_chat_messages_sender_id ON chat_messages(sender_id);"
    # highlight-end
    # ... (indeks lain tetap sama) ...
    index_friendships_sender = "CREATE INDEX IF NOT EXISTS idx_friendships_sender_id ON friendships(sender_id);"
    index_friendships_receiver = "CREATE INDEX IF NOT EXISTS idx_friendships_receiver_id ON friendships(receiver_id);"
    # ... (dan seterusnya untuk indeks lain yang sudah ada)


    try:
        cursor = conn.cursor()
        # ... (cursor.execute untuk tabel-tabel lain) ...
        cursor.execute(sql_create_users_table)
        cursor.execute(sql_create_friendships_table)
        cursor.execute(sql_create_posts_table)
        cursor.execute(sql_create_likes_table)
        cursor.execute(sql_create_comments_table)
        cursor.execute(sql_create_shares_table)
        cursor.execute(sql_create_user_blocks_table)
        cursor.execute(sql_create_post_reports_table)
        cursor.execute(sql_create_notifications_table)

        # highlight-start
        print("Membuat tabel chat_rooms...")
        cursor.execute(sql_create_chat_rooms_table)
        print("Membuat tabel chat_messages...")
        cursor.execute(sql_create_chat_messages_table)
        # highlight-end
        
        print("Membuat trigger...")
        cursor.execute(trigger_update_users)
        cursor.execute(trigger_update_friendships)
        cursor.execute(trigger_update_posts)
        cursor.execute(trigger_update_comments)
        # highlight-start
        cursor.execute(trigger_update_chat_room_last_message_at)
        # highlight-end

        print("Membuat indeks...")
        # ... (cursor.execute untuk indeks lain) ...
        cursor.execute(index_friendships_sender) # Contoh
        # highlight-start
        cursor.execute(index_chat_rooms_users)
        cursor.execute(index_chat_rooms_last_message)
        cursor.execute(index_chat_messages_room_time)
        cursor.execute(index_chat_messages_sender)
        # highlight-end
        # ... (Pastikan semua indeks lama juga dieksekusi)

        conn.commit()
        print("Semua tabel (termasuk chat), trigger, dan indeks berhasil dibuat atau sudah ada.")
    except sqlite3.Error as e:
        print(f"Error saat membuat tabel: {e}")
    finally:
        if cursor:
            cursor.close()

def main():
    # ... (fungsi main sama seperti sebelumnya) ...
    # PENTING: Jika Anda menjalankan ini pada database yang sudah ada,
    # Anda mungkin perlu menghapus file DB lama untuk menerapkan skema baru,
    # atau melakukan ALTER TABLE manual.
    # if os.path.exists(DB_FILE):
    #     print(f"PERINGATAN: File database '{DB_FILE}' sudah ada.")
    #     confirm_delete = input(f"Hapus '{DB_FILE}' untuk membuat ulang dengan skema terbaru (DATA AKAN HILANG)? (ketik 'YA' untuk hapus): ")
    #     if confirm_delete.upper() == 'YA':
    #         os.remove(DB_FILE)
    #         print(f"File database '{DB_FILE}' berhasil dihapus.")
    #     else:
    #         print("Pembuatan database dibatalkan.")
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